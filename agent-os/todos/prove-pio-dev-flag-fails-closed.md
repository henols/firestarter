---
created: 2026-07-28T00:00:00Z
title: Prove the PlatformIO dev-tools build flag fails CLOSED (empirical, not assumed)
area: firmware
resolves_phase: 999.15
files:
  - firestarter/platformio.ini ([env] build_flags — the DEV_TOOLS leak)
  - firestarter/src/dev_tools.cpp (dt_set_registers / dt_set_address — the symbols to check)
  - firestarter/include/firestarter.h (CMD_DEV_ADDRESS / CMD_DEV_REGISTER guards, line 42)
  - .planning/notes/dev-tools-gating-channel-split.md (design this de-risks)
---

## Problem

The channel-split gating design (see `notes/dev-tools-gating-channel-split.md`) needs a
PlatformIO mechanism that turns `DEV_TOOLS` **off by default** and **on only in the dev
environment / pre-release build**. The obvious mechanism is fail-**open** and would silently
defeat the entire feature:

```ini
build_flags = -D DEV_TOOLS=${sysenv.FIRESTARTER_DEV_TOOLS}
```

With the variable unset this plausibly expands to `-D DEV_TOOLS=`, which still **defines** the
macro (as empty), so every `#ifdef DEV_TOOLS` guard stays true and the dev commands leak into
every release build. That is the exact bug class being removed — `-D DEV_TOOLS` currently
leaking from the shared `[env]` block into `uno` / `uno328pb` / `leonardo` *and* `native`.

This must be **measured**, not reasoned about. A design that assumes the expansion behaviour
and gets it backwards ships dev tools in the stable release while all its tests pass.

## Task

Run the matrix and record the result:

1. Try the two candidate shapes:
   - `-D DEV_TOOLS=${sysenv.FIRESTARTER_DEV_TOOLS}` (suspected fail-open)
   - `${sysenv.FIRESTARTER_DEV_FLAGS}` carrying the whole flag, i.e. env var value is
     literally `-D DEV_TOOLS` (suspected fail-closed — the safe shape)
2. For each, build with the variable **set** and **unset**: `pio run -e leonardo`.
3. Do **not** trust the build log or the flash-size delta as the oracle. Check the linked
   binary for the symbols:
   ```bash
   avr-nm .pio/build/leonardo/firmware.elf | grep -iE 'dt_set_registers|dt_set_address'
   ```
   Absent in both = gated. Present with the var unset = fail-open, mechanism rejected.
4. Also confirm `pio test -e native` still passes with `DEV_TOOLS` **absent** — grep says
   nothing under `firestarter/test/` references `DEV_TOOLS` or `CMD_DEV_*`, so this should
   hold, but the shared-`[env]` inheritance means it has never actually been exercised without
   the flag.

## Why symbol-checking, not exit codes

A `pio run` that succeeds proves nothing about whether the guards fired — the guarded code
compiles fine either way. And a flash-size comparison is a weak oracle here: v1.22 Phase 117
already produced a +204 B Leonardo delta that contradicted a size-based prediction
(`project_v122_phase117_closed`). The symbol table is the only direct evidence that
`dev_tools.cpp` did not link.

## Acceptance

- A recorded before/after `avr-nm` capture for the chosen mechanism, both var-set and
  var-unset, on at least one AVR target.
- An explicit statement of which mechanism was chosen and which was rejected, with the
  observed expansion behaviour — so the phase does not re-derive it.

## Item 4 — ANSWERED (v1.22 Phase 119 Plan 02, 2026-07-28)

`pio test -e native_nodevtools` (a new env compiling and running the full 16-suite
`test_filter` without `-D DEV_TOOLS`) passes **112/112 across 16/16 suites**, identical to
`[env:native]`'s baseline, with **zero test-code changes**. This confirms the grep-based
prediction empirically: no test file under `firestarter/test/` references `DEV_TOOLS` or
`CMD_DEV_*`, so the suites are DEV_TOOLS-invariant by construction.

This answers item 4 ONLY. Items 1 through 3 (the `sysenv.FIRESTARTER_DEV_TOOLS` fail-open
vs fail-closed matrix and the `avr-nm` symbol capture) are **untouched** — they remain
scoped to 999.15 / gh#8 and were explicitly out of bounds for Plan 119-02 (LOCK-03/LOCK-02
firmware work), not this item's concern.

**Additional evidence folded in (v1.22 Phase 119 Plan 08/09, 2026-07-28):** RESEARCH's
temporary `[env:leonardo_nodevtools]` measurement at the phase base (commit `1880054`,
before any Phase 119 change) recorded **24388/28672** for a release-config (`-D DEV_TOOLS`
absent) Leonardo build, against `25680/28672` with the flag present — i.e. **`-D DEV_TOOLS`
costs 1292 B** (25680 − 24388) rather than saving it. Since it costs flash, the `DEV_TOOLS`
build carries the SMALLER headroom of the two configurations and is therefore the binding
constraint for LOCK-06's judgement (`.planning/PROJECT.md`'s SIXTH CORRECTION item 3).
This remains evidence for item 4 only (the env now compiles and its tests pass with the
flag absent) — it is not new evidence toward items 1 through 3's fail-open/fail-closed
`sysenv.*` matrix question, which stays open under 999.15 / gh#8. The env itself is now
permanent in `platformio.ini` as `[env:native_nodevtools]` with a CI step, per Plan 119-02.
Items 1 through 3 remain OPEN; this todo stays open pending them.
