---
phase: 199-what-the-rails-can-actually-deliver
plan: 02
subsystem: bench
tags: [bench, rev2.0, leonardo, vpp, vpe, firmware, dev-tools, gh-71]

# Dependency graph
requires:
  - phase: 199-what-the-rails-can-actually-deliver
    provides: "the operator, a Rev 2.0 shield, a Leonardo, and a multimeter — no artifact dependency; this plan measures hardware"
provides:
  - "DELIVERABLE_MAX_DROP_PATH_MV = 17380 — the shipped threshold (D-07), unobtainable any other way"
  - "DELIVERABLE_MAX_DIRECT_VPE_MV = 22140 — what VPE-as-VPP delivers to socket pin 1"
  - "ADC_PAIRED_DROP_MV = 18700 and ADC_PAIRED_DIRECT_MV = 23900, with their signed error figures"
  - "a firmware fix (dt_set_registers re-entrancy) without which no rail can be held on any rig"
affects: [199-03, 199-05]

# Actuals (#2632)
actuals:
  tokens: 34000
  tasks: 3
  commits: 7

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Rail held by the firmware's own dt_set_registers button-wait loop after the host disconnects, rather than by holding the serial port open — supersedes the hold_rail.py method for this rig"
    - "Bounded ADC sampling window (vpp/vpe -t 1) with the sampling rule fixed before the reads are taken"

key-files:
  created:
    - .planning/phases/199-what-the-rails-can-actually-deliver/199-BENCH-RECORD.md
  modified:
    - firestarter_fw/src/dev_tools.cpp

key-decisions:
  - "D-07 resolved against the provisional figure: the operator's provisional 18 V was well-motivated (top of upstream's VPP scale, every capped row capped at it) but 17380 ships. The gap decides the nine algorithm 0x07 rows sitting at exactly 18000."
  - "D-06 honoured: the pin-21 direct-VPE configuration was deliberately not measured, and the record states so alongside the two non-deliberate non-measurements so 199-05 cannot conflate them."
  - "Deviation, scope: a firmware change was made in a milestone that declared one (Phase 201). Operator approved it explicitly after being shown the blocker and the alternatives. It is confined to dev_tools.cpp, which compiles only under -D DEV_TOOLS and therefore ships in no release artifact."
  - "Deviation, method: the plan's hold_rail.py recipe does not hold a rail on this rig and was replaced mid-session. Both windows were measured via dev reg invocations held by the firmware button-wait."
  - "One verify leg left deliberately failing rather than satisfied: 'hold_rail.py 0x088' is absent from the record because Window B was never measured that way. Inserting the string would have made the record lie about provenance."

requirements-completed: []

coverage:
  - id: D1
    description: "The rig is identified, empty and at a known pot setting, every physical fact an operator statement rather than an inference"
    requirement: "RAIL-01"
    verification:
      - kind: manual
        ref: "199-BENCH-RECORD.md § Session setup — port re-probed this session (/dev/ttyACM0, leonardo, 3.0.0b31); Rev 2.0, chip out, pot at max all recorded as operator statements; hw_revision recorded as explicitly non-authoritative"
        status: pass
    human_judgment: true
  - id: D2
    description: "Both VPP paths measured with a meter at socket pin 1, at one pot setting, with the composite that produced each figure recorded"
    requirement: "RAIL-01"
    verification:
      - kind: manual
        ref: "199-BENCH-RECORD.md § Window A (0x188 -> 17.38v/17380) and § Window B (0x088 -> 22.14v/22140)"
        status: pass
    human_judgment: true
  - id: D3
    description: "Paired ADC reads and signed error figures, from bounded windows with a pre-fixed sampling rule"
    requirement: "RAIL-01"
    verification:
      - kind: manual
        ref: "199-BENCH-RECORD.md § Task 3 — VPP 18700 (+1320 mV, +7.59%), VPE 23900 (+1760 mV, +7.95%); both windows emitted two identical frames"
        status: pass
    human_judgment: true
  - id: D4
    description: "dt_set_registers completes instead of destroying its own payload on re-entry"
    verification:
      - kind: integration
        ref: "firmware answers OK: Ready instead of 'Command 8 timed out'; rail confirmed live at socket pin 1 by operator meter"
        status: pass
      - kind: unit
        ref: "pio test -e native (217/217), pio test -e native_nodevtools (217/217)"
        status: pass
    human_judgment: false

# Metrics
duration: 120min
completed: 2026-09-19
status: complete
---

# Phase 199 Plan 02: What the rails actually deliver — measured, after two faults

## Performance

Three tasks. The measurement the plan asked for was obtained, but not by the method the plan
prescribed: that method does not work on this rig and two independent faults had to be found and
one of them fixed before any rail could be energized at all.

## Accomplishments

- **The threshold exists.** `DELIVERABLE_MAX_DROP_PATH_MV = 17380`, measured at socket pin 1 on a
  Rev 2.0 shield with the pot at maximum and the socket empty. D-07 makes this load-bearing: it is
  the shipped figure and cannot be re-derived without another attended session.
- **The rescue is real.** Direct VPE delivers 22140 mV to the same pin. The drop path reaches none
  of the 30 rows; direct VPE covers all ten algorithm `0x07` rows, worst margin 1140 mV.
- **The firmware reads high, by a known amount.** +7.59 % on the drop path, +7.95 % on direct VPE,
  both inside backlog 999.38's 6.8–8.3 % band — independent corroboration of that instrument.
- **Two latent defects found in bench tooling nothing covers.**

## Task Commits

| Task | Commit | Repo |
|---|---|---|
| 1 — rig established | `f4c014d0` | meta |
| (blocked-state record) | `f45c87a1` | meta |
| fix — dt_set_registers | `7eed3af` | firestarter_fw |
| fix — gitlink advance | `15a3e37b` | meta |
| 2 — Window A | `ec23269e` | meta |
| 2 — Window B | `bdefef5e` | meta |
| 3 — ADC pair, limits | `242e1a25` | meta |

## Files Created/Modified

- `.planning/phases/199-what-the-rails-can-actually-deliver/199-BENCH-RECORD.md` (created)
- `firestarter_fw/src/dev_tools.cpp` (modified, 6 insertions / 3 deletions, zero comment lines added)

## Deviations from Plan

### 1. A firmware change, in a milestone that declared one (operator-approved)

The plan is a bench plan and authorizes no source change. `dt_set_registers` had to be fixed or no
rail could be held at all. The operator was shown the blocker, the diagnosis and three options
including abandoning the measurement, and chose the fix. It is confined to `dev_tools.cpp`, which
compiles only under `-D DEV_TOOLS` and ships in no release artifact.

### 2. The prescribed hold method was replaced mid-session

`hold_rail.py` holds no rail on this rig. Both windows were measured via
`firestarter dev reg 0 0 <composite> -f`, held by the firmware's own button-wait loop after the host
disconnected. The record states this explicitly so the `hold_rail.py` strings in it cannot be
misread as the provenance of either figure.

### 3. Window A was opened three times before it produced anything

Recorded in full rather than only the successful attempt: a 300 s window that lapsed before the
operator reached it, and two windows that energized nothing. None was a discarded *reading* — no
reading existed to discard.

## Issues Encountered

**Fault 1 — `hold_rail.py` reports success it never checked.** It prints `RAIL HELD ... 4 bytes
sent` without calling `expect_ack()`, so it cannot observe a refusal. Shipped firmware answered
`ERROR: Unknown command: 8`. `CMD_DEV_REGISTER` is compiled only under `#if DEV_TOOLS`, and
`platformio.ini` sets `-D DEV_TOOLS=1` for `[env:native]` alone — not for `leonardo`, `uno` or
`uno328pb`. **No shipped AVR firmware implements `firestarter dev reg`, `dev addr` or this script.**
It historically sat in the shared `[env]` block (fw `2678306`), which is why the method worked at the
v1.14 and v1.18 benches and silently stopped. `firestarter dev reg` also **exits 0** on this path
while printing the error.

**Fault 2 — `dt_set_registers` was not re-entrant across its own early return.** It consumed the ACK
via `op_get_message`, then returned `false` if the 4 payload bytes had not yet arrived — routine,
since the host sends ack and payload as separate writes. On re-entry the ACK was gone, so
`op_get_message` ran over the payload `00 00 81 88`, where every byte falls to its `default:` arm
and is read and discarded as junk. Payload destroyed, handler spinning, firmware timeout. Fixed with
a bounded wait on a `TIMEOUT_MS` deadline; a genuinely absent payload still ends in the same timeout
error, so no failure mode is hidden.

**Two of this plan's four Task 2 verify legs do not pass.** One true negative, left failing (see
Deviations 2). One false positive: `test -z "$(pgrep -af hold_rail.py)"` matches the verify script's
own command line, because the preceding leg contains the literal string and both run in one shell.
It fails closed, which is the safe direction. Full disposition table in the bench record.

**Device-node permissions.** After one re-enumeration the node returned as `crw------- root root`
instead of `crw-rw-rw-+ root dialout` and could not be opened; restored with `chgrp dialout` +
`chmod 660`. The node also moved `ttyACM0 -> ttyACM1 -> ttyACM0` across the session, which is why
standing bench rule 1 requires re-probing identity rather than inheriting it.

## Numeric Results

```
DELIVERABLE_MAX_DROP_PATH_MV = 17380
DELIVERABLE_MAX_DIRECT_VPE_MV = 22140
ADC_PAIRED_DROP_MV = 18700
ADC_PAIRED_DIRECT_MV = 23900
```

| Rail | Monitor | Meter at pin 1 | Difference | Share of meter |
|---|---|---|---|---|
| Drop-resistor / VPP | 18700 mV | 17380 mV | +1320 mV | +7.59 % |
| Direct VPE | 23900 mV | 22140 mV | +1760 mV | +7.95 % |

## User Setup Required

**The attached board no longer runs shipped firmware.** It carries a locally built `[env:leonardo]`
image with `-D DEV_TOOLS=1` that self-reports as `3.0.0b33` and is **not** the released `3.0.0b33`.
Restore with `firestarter fw --install` when the bench work is finished.

## Next Phase Readiness

`199-03` can now fill `DELIVERABLE_MAX_DROP_PATH_MV` from this record. `199-05` can claim a measured
threshold, and owes its reader the D-06 approximation disclosure: the 20 algorithm `0x0B` rows take
VPE to **pin 21**, which was deliberately not measured, so no figure here adjudicates the six rows
at 25000 mV.

## Self-Check: PASSED

Bench record exists and carries all four parseable figure lines. All seven commits found in
`git log --oneline --all` in their respective repos. Both repos on `v1.40-program-parameter-fidelity`.
Comment check clean on the firmware commit. `native` and `native_nodevtools` 217/217 each.
