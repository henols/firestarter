---
artifact: SAFE-01-PREFLIGHT
phase: 97-pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program
milestone: v1.18 — AM27C020 0x08 Write-Path RCA & Fix
requirements: [SAFE-01]
status: CONFIRMED (non-invasive code-read) — guards intact, never triggered
recorded: 2026-06-29
operator_witnessed: n/a (pure code-read, no hardware, no guard triggered)
branch_base: firmware bccd995 (v1.17 tip) · host e0bdea4
---

# SAFE-01 Non-Invasive Pre-Flight Confirmation (Phase 97)

> **Method:** code-READ only. No VPP was driven high, no guard was invoked, no
> escape hatch was added, and no source was edited. This note records the four
> SAFE-01 confirmations from 97-RESEARCH.md §"SAFE-01 Non-Invasive Verification
> Steps", per CONTEXT.md decision **D-07**, each with a `file:line` citation
> verified against the **current tree** (firmware `bccd995`, host `e0bdea4`) this
> session — NOT copied blindly from the RESEARCH line numbers.
>
> SAFE-01 here is a **confirmation artifact**, not an action. It recurs as a
> standing precondition through Phases 98–99.

---

## Confirmation 1 — Over-voltage stays ERROR-blocked (firmware)

The shared VPP window-compare body is `vpp_check_window` at
`firestarter/src/proms/primitives.cpp:93`.

- **HIGH branch (over-voltage):** the test `vpp_mv > handle->vpp_mv + 500` at
  `primitives.cpp:106` enters the over-voltage block. Inside, the disposition
  forks at `primitives.cpp:121`:
  - `if (is_flag_set(FLAG_FORCE))` → `RESPONSE_CODE_WARNING` (`primitives.cpp:123`)
  - `else` → `RESPONSE_CODE_ERROR` (`primitives.cpp:126`, with `LOG_ERROR_ID_BYTES(MSG_ERR_VPP_HIGH, …)`)

  So the over-voltage path is **ERROR-blocked by default** and relaxes to a
  WARNING **only** when `FLAG_FORCE` is set.

- **IMPORTANT NUANCE (the real shape of the invariant):** the firmware DOES
  contain a `FLAG_FORCE` relaxation of the HIGH branch (`primitives.cpp:121-127`).
  The SAFE-01 invariant is therefore satisfied **NOT** by the firmware lacking a
  relaxation, but by the **Phase-97 bench procedure NEVER passing `--force` /
  `FLAG_FORCE`** on the AM27C020 write attempt. The over-voltage ERROR is the
  enforced default; the procedure simply never opts into the relaxation. This is
  stated explicitly so a later reader does not mistake "FLAG_FORCE exists" for a
  SAFE-01 hole — the hole would be a *procedure* that uses it, and none does.

- **LOW branch (under-voltage):** `vpp_mv < handle->vpp_mv * 95 / 100` at
  `primitives.cpp:129` sets `RESPONSE_CODE_WARNING` (`primitives.cpp:145`,
  `MSG_WARN_VPP_LOW`) and the firmware **proceeds**. This is WARNING/proceed-only —
  there is no ERROR and no block on a low rail.

- **Connection to Pitfall 2 (silent under-program):** because a low VPP rail is
  only a WARNING and the firmware proceeds, an under-voltage rail will
  **silently under-program with no error** ("0 bits, no error"). This is exactly
  why the **pin-1 DMM measurement in Plan 02 is mandatory** before trusting any
  write verdict — the firmware cannot tell us the rail magnitude is wrong, only a
  physical measurement at the socket can. (See also Confirmation 4.)

---

## Confirmation 2 — Host guard never bypassed

The live-path guard is `resolve_chip` at
`firestarter_app/firestarter/chip_resolver.py:16` — the single chokepoint between
CLI dispatch and the EPROM database lookup/conversion. It raises
`ChipNotImplementedError` for any `support_status != "supported"` chip **before**
`convert_to_programmer` builds any wire dict or any serial byte is emitted
(`chip_resolver.py:51-57`).

The Phase-97 / Plan-02 / Plan-03 bench procedure uses plain `firestarter write` /
`firestarter dev …` invocations:

- **NO test-only flag** — the program attempt is a normal `firestarter write AM27C020 <probe.img>`.
- **NO `-b` skip-erase / skip-blank abuse** — `-b` is not used to force the write through a guard.
- **NO escape-hatch argument** — there is no path in the procedure that bypasses
  `resolve_chip` or relaxes a guard to "make a write succeed".

`resolve_chip` therefore stays in the live write path for AM27C020 throughout the
RCA, exactly as for any normal program operation.

---

## Confirmation 3 — Normal `0x08` dispatch, zero code edits

AM27C020 (`protocol 0x08`) flows through normal dispatch with **no special-case**:
`firestarter/src/proms/memory.cpp:121` matches
`protocol == 0x07 || protocol == 0x08 || protocol == 0x0B` and calls
`configure_eprom(handle)` at `memory.cpp:122`. There is no `0x08`-specific
detour, no test branch, and no escape path.

Phase 97 is **diagnostic only** — it introduces **ZERO firmware/host source
edits**. All Phase-97 task work writes only into `.planning/**` artifact files;
no file under `firestarter/` or `firestarter_app/` is modified.

---

## Confirmation 4 — Manual-potentiometer caveat (D-07)

The shield VPP **magnitude is operator-set on the manual potentiometer**; the
firmware can only **enable the regulator and measure the ADC node** — it cannot
set the rail level. Consequence: a low pot setting produces a silent
under-program (Confirmation 1, LOW branch = WARNING/proceed-only), so the
firmware's own VPP check **cannot** prove the rail is correct.

Therefore the **pin-1 DMM (Plan 02) is the only proof the rail magnitude actually
reaches the chip at 12.5–13.0V** — a SAFE-01-adjacent reason a measured rail is
mandatory before any write verdict. The operator must also physically confirm the
pot setting each session.

---

## Bypass-command gate (Task 1 `<verify>`)

The `<verify>` gate scans the three Phase-97 PLAN files and this artifact for an
actual bypass **command invocation** — a `firestarter write|dev … --force` or
`… -b` carrying a bypass flag for the AM27C020 write — and passes only if none is
present. The gate deliberately matches real command invocations, **not** free-text
mentions of the words "--force" / "FLAG_FORCE" / "bypass", so this note's
legitimate SAFE-01 prose (which must discuss those terms to document the
invariant) does not trip it, while a genuine bypass command anywhere in the plans
or this artifact would still fail it.

---

## SAFE-01 Phase-97 Verdict

| Item | File:line | Verdict |
|------|-----------|---------|
| Over-voltage HIGH → ERROR (default) | `primitives.cpp:106,121,126` | GREEN — ERROR-blocked, relaxes to WARNING ONLY under FLAG_FORCE; procedure never passes FLAG_FORCE |
| Under-voltage LOW → WARNING (proceed) | `primitives.cpp:129,145` | NOTED — silent-under-program risk; pin-1 DMM mandatory |
| Host guard in live path | `chip_resolver.py:16,51-57` | GREEN — `resolve_chip` never bypassed; no test flag / no `-b` skip / no escape hatch |
| Normal `0x08` dispatch | `memory.cpp:121-122` | GREEN — no special-case; zero code edits in Phase 97 |
| Manual-pot caveat | (D-07) | NOTED — rail magnitude operator-set; pin-1 DMM is the only proof |

**SAFE-01 confirmed non-invasively. No guard was triggered or relaxed; the
Phase-97 procedure is proven bypass-free.**
