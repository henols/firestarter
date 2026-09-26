---
title: dev test — sequence cost model and where the time actually goes
date: 2026-08-30
context: Captured during /gsd-explore 2026-08-30, from the operator's question "there are so many reads, what's the point of doing it that way?" Records the measured primitive costs, the validated connect model, and the four waste patterns found in chip_test.py, so a future planner does not have to re-derive them. Companion to seed dev-test-adaptive-sequencing.md, todo 2026-08-30-gate-fingerprint-readback-on-step-failure.md, and Backlog 999.43. Executable model: dev-test-sequence-cost-model.py (same directory).
---

# `dev test` — sequence cost model

## Provenance of the numbers

Every rate here comes from **one** operator log: a single
`firestarter dev test sst27sf512 --fast` run on a **Leonardo** (1024 B buffer)
against a **65536 B** part, pasted into the explore session on 2026-08-30. This
is a model built on one sample, not a benchmark. An Uno's 512 B buffer will
produce different rates and the model should be re-measured before it is trusted
on another board class. `erase` is treated as flat because one data point cannot
say whether it scales with device size.

The **connect model** is a stronger claim, because it is derived structurally
from the code rather than fitted to the log — and it then reproduces the
observed count exactly (**13 predicted, 13 observed**). Its per-connect *cost*
is unmeasured: `/dev/ttyACM0` was in use during the session, so the model reports
counts only and no seconds are attributed to connection overhead anywhere below.

**⚠ Correction, second data point, same day.** An `AM27C020` run (262144 B,
protocol `0x08`, same Leonardo) read at **7.0 KB/s** — 37.24s and 37.22s across
two runs — against the **8.7 KB/s** this model derives from the 64 KiB `0x07`
part. **Read rate varies by protocol, not only by size**, and the model
therefore *over-predicts* read speed by ~24% on `0x08`. Every read-derived
figure below and in the companion script is a `0x07` figure. The direction of
the error is safe for the argument the model is used to make — reads are even
more dominant than stated — but no absolute second-count here should be quoted
for a non-`0x07` part without re-measuring. The same run also invalidates its
own total as a comparison point: it aborted after one cycle (see the write-init
blank-check defect, Backlog 999.44), so its 114.0s is not the modelled 99.6s
two-cycle run.

## Measured primitives (65536 B part)

| Primitive | Time | Effective rate | Wire direction |
| --- | --- | --- | --- |
| **read** | 7.51s | 8.7 KB/s | device→host, plus a host file write |
| **verify** | 5.71s | 11.5 KB/s | host→device, **firmware compares** |
| **blank-check** | 4.86s | 13.5 KB/s | no payload, device-side scan |
| **erase** | 5.15s | — | no payload |
| **write** | 30.04s | 2.2 KB/s | host→device plus programming |
| **chip-ID** | 0.28s | — | — |

**The single most useful fact in this table: `read` is the most expensive
non-write primitive there is.** `verify` covers the same bytes 24% cheaper and
`blank-check` 35% cheaper, because neither ships the payload back to the host or
writes a file. Any full-device read that could have been a verify or a
blank-check is pure loss.

`write` at 2.2 KB/s is 65% of a full-device run on its own. That is the per-byte
VPE settle path — a firmware concern, already root-caused elsewhere, and **not**
addressable by resequencing. Nothing in this note or its companions claims to
improve it.

## Why verify can replace a read-back, and where it cannot

`verify_eprom` streams host→device and the firmware compares
([`memory.cpp:377-396`](../../firestarter/src/proms/memory.cpp#L377-L396)). On a
mismatch it emits `MSG_ERR_VERIFY` carrying `expected`, `actual` and a 3-byte
address — then **returns immediately**. So:

- As a **pass/fail oracle**, verify is complete and 24% cheaper than a read-back.
  A failing verify is also *faster* than a passing one, because it early-returns.
- As a **diagnostic**, verify gives exactly one data point. It cannot produce the
  mismatch *distribution* — and the distribution is the whole input to
  `classify_fingerprint`: bit-clustering across many offsets is what separates an
  address-line fault from a contact fault, and `ff_ratio` across the buffer is
  what detects a false PASS.

That asymmetry is the design seam. **Verify decides; a read-back diagnoses; the
read-back only needs to run when verify says something is wrong.**

## The four waste patterns

### 1. The fingerprint read-back is unconditional on outcome

[`chip_test.py:3100`](../../firestarter_app/firestarter/chip_test.py#L3100) gates
on op membership and final-cycle only — it never consults `outcomes`. On a
passing run it performs two full-device reads to characterise a mismatch set
that is empty by construction.

The `ff_ratio` false-PASS check is the reason it was written unconditional
(`classify_fingerprint`'s bucket 1 is checked "regardless of whether there are
zero mismatches (a perfect verify)",
[`chip_test.py:197-199`](../../firestarter_app/firestarter/chip_test.py#L197-L199)),
and that concern is real for the **write** step. But it is already answered for
free: a write that reports OK without driving the bus is caught by the **verify
step that immediately follows it in the same cycle**, at no extra cost.

### 2. The post-verify read-back duplicates the firmware's own compare

By the time the second read-back runs, `verify_eprom` has already compared the
identical `expected` buffer on-device. On any run that reaches this point with a
passing verify, `bad` is guaranteed 0.

### 3. The read step buys one boolean for two full sweeps

[`_dispatch_read`](../../firestarter_app/firestarter/chip_test.py#L2626) reads
the whole device `runs` times into a `TemporaryDirectory`, sha256s each, and
keeps only the divergence record. The contents are discarded — so despite
running before every destructive step, **it is not a pre-write backup**, and its
only surviving output is "did the two hashes differ".

### 4. The sampler costs 4 connects per write step

[`_make_sampler`](../../firestarter_app/firestarter/cli_handlers.py#L2194) calls
`sample_vpp_mv()` then `sample_vpe_mv()` as two separate
`hardware_manager` calls, each opening and tearing down its own connection, at
both the `before` and `after` phases. This is the 3-connect cluster that appears
immediately before each write in the operator's log.

Every connect is a `_setup_operation` →
[`find_and_connect`](../../firestarter_app/firestarter/serial_comm.py#L943) →
`_disconnect_programmer` round trip; `EpromOperator.comm` is torn down after
every call by design.

## Where the reads go (sst27sf512, default `runs=2`)

Plan: `id`, `read`, then the cycle block `[write, verify, erase, blank-check]`
run twice, plus six NA SDP steps.

| # | Read | Bytes | When | Unique information it produces |
| --- | --- | --- | --- | --- |
| 1–2 | read step, 2 runs | 2 × 64K | always | run-to-run divergence (transport nondeterminism) |
| 3 | fingerprint read-back after write | 64K | final cycle, unconditional | mismatch distribution — only if the write failed |
| 4 | fingerprint read-back after verify | 64K | final cycle, unconditional | nothing the firmware compare did not already establish |

Modelled total ≈ **121.8s**, of which ≈ 37.5s (31%) is reads and ≈ 22.5s of that
produces nothing on a passing run.

## Connect counts (structural, validated)

| Chip | Connects, `runs=2` |
| --- | --- |
| sst27sf512 | 22 |
| at28c256 (SDP leg) | **32** |
| m27c512 | 22 |
| am27c020 | 22 |
| w29c040 | 18 |

AT28C256 is the outlier: its six-op SDP leg costs **12 connects for roughly 3 KB
of traffic**, because each leg op is a write plus a `_read_region`. The leg is
overhead-dominated, not bandwidth-dominated — the opposite of every other part
of the plan.

## Plans as derived, per chip class

Confirmed by calling `derive_plan(chip, db, write_scope="full")` directly:

| Chip | electrical-type | alg | Write region | Policy | Notes |
| --- | --- | --- | --- | --- | --- |
| sst27sf512 | EEPROM | 7 | (0, 65536) | full-device | erase + blank-check both live |
| at28c256 | EEPROM | 13 | (0, 32768) | full-device | id NA, blank-check NA, 6 live SDP steps |
| m27c512 | UV-EPROM | 7 | (65280, 256) | uv-slot | erase NA, blank-check before write, uv-tranche payload |
| am27c020 | UV-EPROM | 8 | (261888, 256) | uv-slot | as above; 256 KiB device, 256 B write |
| w29c040 | Flash/EEPROM | 5 | (16384, 491520) | full-device | boot blocks carved out, erase NA, blank-check NA |

The UV rows are where the imbalance is starkest: a **256-byte** write on a
**256 KiB** part, where essentially the entire run is preflight overhead.

## What this note does not establish

- Whether `erase` scales with device size.
- Anything about the write path's 2.2 KB/s, which is firmware-side.

Per-connect cost in seconds, and the Uno-class-board rate, were both unestablished when this note
was written (port busy; counts only). Both are now measured, per board class, never blended, in
[`176-MEASUREMENT.md`](../phases/176-transport-instrumentation-connect-cost-measurement-partially/176-MEASUREMENT.md).
