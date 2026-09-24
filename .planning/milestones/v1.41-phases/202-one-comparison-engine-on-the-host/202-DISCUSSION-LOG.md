# Phase 202: One comparison engine, on the host - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-20
**Phase:** 202-one-comparison-engine-on-the-host
**Areas discussed:** Streaming engine shape & home, The no-abort tail, Mismatch vs failure, Report format & region rules

---

## Streaming engine shape & home

### Where the engine lives

| Option | Description | Selected |
|--------|-------------|----------|
| New `firestarter/compare.py` | Import-light like `chip_test`. Preserves the existing one-way import graph; costs one new module. | ✓ |
| Inside `eprom_operations.py` | No new file, but `chip_test.py` would have to import a 2502-line module pulling `serial_comm`. | |
| Inside `chip_test.py` | Diff primitives already there, but `eprom_operations` gains an import of a 3774-line module pulling `chip_resolver` → `database`. | |

**User's choice:** New `firestarter/compare.py`
**Notes:** Neither big module imports the other today, and `chip_test.py:113-117` documents that as deliberate.

### How far to design the interface

| Option | Description | Selected |
|--------|-------------|----------|
| Build for all three consumers now | Phase 203's `write --verify` and Phase 206's `dev test` drop in without reshaping. Separates compare-and-return from render-report. | ✓ |
| Minimal for verify/blank; extend later | Less speculation, but 203 is the very next phase and the widening is near-certain. | |
| You decide | Defer to the planner. | |

**User's choice:** Build for all three consumers now

### Decided by precedent, not asked

Two questions were settled from existing code rather than put to the user, per the standing preference
to decide mechanical gray areas where a precedent settles them:

- **Streaming accumulator vs a parallel classifier** — `chip_test.py:113-117` states "do NOT add a
  second parallel divergence implementation" as a source rule. `classify_fingerprint` delegates to
  the accumulator.
- **Expected-side supply** — a pull callback `expected(offset, length) -> bytes`, matching
  `_main_phase_read_data`'s existing `(address, payload)` push callback.

---

## The no-abort tail

The first question offered three variants of "the bytes arrive anyway, so comparing them is free".
The user rejected all three and asked for a real abort: *"stop comparing tell the programmer to break
and stop sending more bytes."* That is CMP-F1, which the roadmap had filed as deferred, so the
mechanism was researched in the firmware source before the decision was captured.

**Research finding:** a mid-stream stop already works within the existing protocol, unchanged.
`op_wait_for_ack` (`operation_utils.cpp:94-108`) times out after 1000 ms and returns false; that
propagates to `loop()` running `command_done()` (`firestarter.cpp:208-217`), which zeroes the
registers and returns to `CMD_IDLE`. The roadmap's premise — that the END phase must run to leave the
port clean — was too pessimistic: `command_done()` is what performs the teardown, and it runs on the
error path too.

### How to break the read

| Option | Description | Selected |
|--------|-------------|----------|
| Stop acking — app-only | Firmware times out ≤1 s, `command_done()` leaves the port clean. Phase stays app-only/bench-no. Cost: ≤1 s, and a deliberate abort looks like a real timeout on the wire. | ✓ |
| Send `DONE` mid-read | One-line firmware change to `op_wait_for_ack`; immediate and unambiguous. But puts firmware work in an app-only, bench-no phase. | |
| Stop acking now, `DONE` in 204 | Ship the app-only route, fold the firmware line into the already-dual-repo Phase 204. | |

**User's choice:** Stop acking — app-only, no firmware change
**Notes:** The `DONE` variant was captured as a deferred idea for Phase 204 rather than dropped.

### The aborted path's fingerprint

| Option | Description | Selected |
|--------|-------------|----------|
| Bucket, labelled with the compared range | Bucket over the bytes actually compared, always printed with the explicit range so it cannot read as a whole-chip verdict. | ✓ |
| Suppress confident buckets on a partial compare | Cannot mislead, but discards a real signal when the prefix is large. | |
| No fingerprint on default; `--full` only | Clean story, but reads against CMP-06 and criterion 4. | |

**User's choice:** Bucket, labelled with the compared range
**Notes:** Raised because `classify_fingerprint` checks `blank/contact` first on an `0xFF` ratio ≥ 0.98, so a short mostly-`0xFF` prefix could otherwise produce a confident label from a truncated sample.

---

## Mismatch vs failure

### Exit codes

| Option | Description | Selected |
|--------|-------------|----------|
| Exit 2 for transport/hardware | `diff(1)`/`cmp(1)` convention and the in-repo `consistency_check_eprom` precedent. Collides with Click's `UsageError` = 2. | ✓ |
| Exit 3 | No Click collision, but departs from the convention CMP-07 is written against. | |
| Keep exit 1, message only | Nothing scriptable can branch on it. | |

**User's choice:** Exit 2 for transport/hardware

### SRAM/FRAM `blank`

| Option | Description | Selected |
|--------|-------------|----------|
| Refusal code, same as trouble | Inapplicable is not "not blank". Exits 2. | ✓ |
| Keep exit 1, unchanged | No compat risk, but keeps the conflation. | |
| Out of scope — file it | Leave it alone and backlog the semantics. | |

**User's choice:** Refusal code, same as trouble
**Notes:** Checked before asking — `derive_plan` marks SRAM/FRAM blank-check NA up front (`chip_test.py:341-348`) and never reaches the short-circuit, so `dev test` is unaffected.

### Blast radius

| Option | Description | Selected |
|--------|-------------|----------|
| `verify` + `blank` only; file the rest | Minimal blast radius; matches CMP-07's wording. | ✓ |
| Change `map_typed_errors` globally | Consistent CLI, but silently alters ~20 commands including `write`. | |
| Global mechanism, opt-in list | Machinery now for an unscheduled migration. | |

**User's choice:** `verify` + `blank` only; file the rest

---

## Report format & region rules

### `--full` range list bound

| Option | Description | Selected |
|--------|-------------|----------|
| Cap the list, keep exact counts | Retain up to N ranges, then a tail line from running counters. Bounded memory and output; totals stay exact. | ✓ |
| Stream each range as it closes | Genuinely O(1), but unbounded output and nothing to return to `dev test`. | |
| Retain every range | Simplest, but peak memory scales with device size in the pathological case. | |

**User's choice:** Cap the list, keep exact counts

### Report verbosity

Asked twice. The first question offered two lines / two lines plus hexdump / one line. The user
answered freeform: *"one line, start addess, stop address and numer of bytes"* — a range form rather
than any option offered. A follow-up presented three concrete rendered previews of that shape; the
user answered freeform again: *"range , number of bytes and dont show any real bytes"*.

| Option | Description | Selected |
|--------|-------------|----------|
| Range + bytes + bucket, one line | Everything on one line; satisfies CMP-04 and CMP-06. | |
| Range + bytes only; bucket on its own line | Shorter lines, two lines on a default failure. | |
| Range + bytes only, no bucket line | Tersest; drops the fingerprint entirely. | |
| *(user's own form)* | `Mismatch 0xSTART-0xEND (N bytes)` — no expected or actual byte values. | ✓ |

**User's choice:** Range and byte count only, no byte values
**Notes:** The conflict with CMP-04 ("its absolute address, the expected value and the value read") was stated in the question before the answer was given, and again after. See the CMP-04 disposition below.

### Bucket line

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, one summary line after the ranges | Keeps CMP-06 and criterion 4 met. | ✓ |
| Only under `-v` | Tersest, but needs the same amendment as CMP-04. | |
| Not at all | Leaves CMP-06 unmet on the CLI surface. | |

**User's choice:** Yes, one summary line after the ranges

### CMP-04 disposition

| Option | Description | Selected |
|--------|-------------|----------|
| Amend REQUIREMENTS.md now | Requirement and code agree; traceability stays honest at close. | ✓ |
| Leave CMP-04, record as knowingly unmet | The v1.40 PULSE-04/RAIL-03 pattern; honest but leaves a requirement nobody intends to meet. | |
| Let the planner decide | Hand the conflict downstream. | |

**User's choice:** Amend REQUIREMENTS.md now

### Region resolution

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit wins, conflicts refuse | `--size` wins; short file is a usage error; over-run refused before the port opens. | ✓ |
| Compare the overlap silently | Never errors, but `verify -s 64K` against a 4K file would report a clean match. | |
| Warn and clamp | Proceeds with both numbers named, v1.40 D-4 shape. | |

**User's choice:** Explicit wins, conflicts refuse

---

## Claude's Discretion

- The cap value `N` for `--full`'s retained range list, and the bounded acceptance window for
  recognising the host's own deliberate `MSG_ERR_TIMEOUT`.
- Internal shape of the streaming accumulator (class vs closure).
- Exact wording and capitalisation of the two output lines.
- Progress-bar behaviour for `blank` and on an aborted run — offered as a gray area and declined.

## Deferred Ideas

- A clean `DONE`-based mid-read stop, one line in `op_wait_for_ack`. Best home: Phase 204. A cheaper
  route to CMP-F1 than the protocol-level abort that requirement assumes.
- CLI-wide exit-code consistency for the other ~20 commands still exiting 1 on transport failure.
- Progress-bar behaviour during `verify` and `blank`.
- Harness work for criteria 1 and 2 — a wire-level assertion that neither ordinal is sent, and a
  peak-memory measurement on a 512 KB part. Neither has an obvious existing home.

## Areas offered and declined

At the close prompt the user selected "I'm ready for context" over three further candidate areas:
proving criteria 1 and 2, progress-bar behaviour, and what stays behind until Phases 204/205. All
three are recorded above as deferred rather than dropped.
