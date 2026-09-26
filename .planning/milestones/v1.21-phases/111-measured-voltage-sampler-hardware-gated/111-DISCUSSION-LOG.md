# Phase 111: Measured-Voltage Sampler (hardware-gated) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-02
**Phase:** 111-measured-voltage-sampler-hardware-gated
**Areas discussed:** Rail & report slot, Sampling count, Timing & non-destructive, Bench-validate vs defer

---

## Rail & report slot

| Option | Description | Selected |
|--------|-------------|----------|
| Protocol-relevant rail + label | Sample the rail this chip's write uses (VPP for 0x07/0x08; VPE for 0x0B), one value + rail label in the existing slot | |
| Both rails, two fields | Always sample VPP AND VPE, split the report into vpp_mv + vpe_mv | ✓ |
| VPP only (fill slot as-is) | Sample just VPP into the one slot | |

**User's choice:** Both rails, two fields
**Notes:** Expands the Phase-110 single `vpp_vpe_mv` slot into separate VPP/VPE fields (in-remit — Phase 110 explicitly left the slot). Avoids a protocol→rail mapping that could go stale and rules out "wrong rail energized"; costs two serial round-trips per rail.

---

## Sampling count

| Option | Description | Selected |
|--------|-------------|----------|
| N samples → median (N=3–5) | A few frames from the read loop, report the median mV | ✓ |
| Single reading | One frame per rail | |
| N samples → min | Worst-case (lowest) rail across N samples | |

**User's choice:** N samples → median (N=3–5)
**Notes:** Robust against a single transient misread (the project's VPP-misread history). Exact N and whether to record the raw sample count left to planner's discretion.

---

## Timing & non-destructive

Two coupled decisions in this area — timing relative to the write, then non-destructive-run behavior.

### Timing relative to the write

| Option | Description | Selected |
|--------|-------------|----------|
| Before the write (baseline) | Sample both rails once, right before write_eprom | |
| After the write | Sample after write_eprom returns | |
| Both before & after | Bracket the write with two independent regulator reads | ✓ |

**User's choice:** Both before & after
**Notes:** The VPP/VPE read is a self-contained command and write_eprom is self-contained — before/after are two INDEPENDENT energizations bracketing the write, not two points on one pulse. Gives across-write change/droop signal (4 sample points on a destructive run).

### Non-destructive-run behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — one standalone rail read | Single VPP+VPE read even with no write; safe (regulator-only, no socket routing) | ✓ |
| No — NOT_MEASURED | Strict VOLT-01: sampler wired only into the write step | |

**User's choice:** Yes — one standalone rail read
**Notes:** Safe with a chip seated (memory `reference_vpp_vpe_no_socket_routing`). Gives every tester a "can my rig reach VPP/VPE?" data point without spending a chip; fits the community tool + Phase-109 "only N of M ran" story. Before/after slots read NOT_MEASURED on a non-destructive run.

---

## Bench-validate vs defer

| Option | Description | Selected |
|--------|-------------|----------|
| Software-complete + defer bench | Build + unit-test vs synthetic 0xE4/0xE5 frames now; defer live SC2 to a bench session (HUMAN-UAT/FUT) | ✓ |
| Bench-validate this session | Run live on Leonardo + Rev 2.0, confirm sampled mV == printed monitor value | |

**User's choice:** Software-complete + defer bench
**Notes:** Matches the v1.17/v1.18 software-complete + hardware-deferral precedent and the milestone's "isolate the one hardware-gated phase" framing. Phase 112 proceeds on the sampler API immediately; the live validation is a documented, light bench procedure deferred to an operator bench session.

## Claude's Discretion

- Exact mV computation from the `%u.%uV` (whole/frac) 4×u16 frame — parse raw payload via `frame_parser._decode_param`; confirm fractional scaling. Flagged as the likely `--research-phase 111` item.
- Additive-sibling refactor (single-frame parse helper); MUST NOT change `_read_voltage_loop`'s printing/loop behavior (SC3).
- Exact N (3–5), whether to record raw samples, flat-vs-nested voltage field shape.
- `flags` passed to the read command (default 0 unless research surfaces a need).

## Deferred Ideas

- SC2 live hardware validation (Leonardo + Rev 2.0) — deferred to a bench session as a HUMAN-UAT / FUT item (per the bench decision). Light procedure documented in CONTEXT.md D-05.
- Todo matcher's 8 matches (1 @ 0.9 firmware VPP-check, 7 @ 0.6) — all off-axis for a host-only frame-parse phase; none folded (same disposition as Phases 109/110).
