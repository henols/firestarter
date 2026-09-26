# Phase 119: LOCK — SDP-enable + command surface (FW half) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-28
**Phase:** 119-LOCK — SDP-enable + command surface (FW half)
**Areas discussed:** Todo fold; Admission guard + fail-closed reach; Lock table + the frozen shared header; What a standalone lock reports; LOCK-06 headroom + page-load measurement

---

## Todo fold — `prove-pio-dev-flag-fails-closed.md` (999.15)

| Option | Description | Selected |
|--------|-------------|----------|
| Fold item 4 only | Prove `pio test -e native` passes with DEV_TOOLS absent — LOCK-03's actual prerequisite. Items 1–3 stay in the 999.15 backlog note. | ✓ |
| Fold the whole todo | Also run the `${sysenv.*}` fail-open/fail-closed matrix with `avr-nm` symbol captures and pick the gating mechanism here. | |
| Fold none | LOCK-03's test stands entirely on its own; the todo stays untouched. | |

**User's choice:** Fold item 4 only.
**Notes:** Keeps the phase FW-scoped. The release-channel gating mechanism stays with 999.15 / gh#8.

---

## Admission guard + fail-closed reach

### Q1 — `is_memory_cmd()` and the cmd 7/8 side effect

| Option | Description | Selected |
|--------|-------------|----------|
| Tighten, and own it | Enumerate the memory commands; a release build stops calling `configure_memory` for cmd 7/8; recorded as a deliberate safety tightening. | ✓ |
| Tighten + honest refusal for 7/8 | As above, plus an explicit `MSG_ERR_NOT_SUPPORTED` for 7/8 in a no-DEV_TOOLS build instead of `MSG_ERR_UNKNOWN_CMD`. | |
| Preserve today's behaviour exactly | Make the predicate itself `#ifdef DEV_TOOLS`-conditional — zero behaviour delta, but re-creates the divergence LOCK-03 removes. | |

**User's choice:** Tighten, and own it.
**Notes:** Discovered during the question's framing: the guard at `firestarter.cpp:79` is `#ifdef DEV_TOOLS`-conditional, so a release build already runs `configure_memory` for dev commands it will refuse.

### Q2 — Where the SDP-command protocol gate lives

| Option | Description | Selected |
|--------|-------------|----------|
| One guard at the op layer | NULL `main` ⇒ `MSG_ERR_NOT_SUPPORTED`. One site, smallest flash, provably total. | ✓ |
| Pre-dispatch check in `configure_memory` | Refuse SDP commands for `protocol != 0x0D` before the protocol chain. | |
| `default:` arm in every `configure_*` handler | Six sites; most self-documenting, most flash. | |
| Op-layer guard + selective `0x0D` `default:` | Both, at two sites. | |

**User's choice:** One guard at the op layer.
**Notes:** Surfaced before asking: `configure_memory` pre-sets the generic `main` for READ/WRITE/VERIFY at `memory.cpp:48-58`, so a literal `default:` arm in `configure_eeprom28c` would refuse `read` and `verify` on all 84 `0x0D` chips. LOCK-04's stated mechanism is therefore superseded; its intent is preserved.

### Q3 — Proving DEV_TOOLS invariance

| Option | Description | Selected |
|--------|-------------|----------|
| Second native env | `[env:native_nodevtools]` running the same truth-table suite — a semantic proof; discharges the folded todo item 4. | |
| One env, `#undef` / re-include trick | Single TU includes the predicate twice; cheapest, but proves a construct, not the real build. | |
| Host-side source-scan gate | AST gate asserting no `#ifdef` inside the predicate, with a planted-violation fixture. | |
| Second native env + source-scan gate | Both — semantic proof plus structural protection against reintroduction. | ✓ |

**User's choice:** Second native env + source-scan gate.
**Notes:** Consequence owned as task work: the new gate joins the CORRECTION-4-item-4 cross-repo checklist for Phases 120–122, and the new env needs its own `test_filter` plus a CI job line.

### Q4 — How wide the NULL-`main` guard reaches

| Option | Description | Selected |
|--------|-------------|----------|
| SDP commands only | Guard lives in the new SDP op path; DEVTEST-01 stays wholly in Phase 121. | |
| Generic — fix the whole class now | One refusal in the shared path; fixes SDP, erase and chip-ID phantom-success together. | ✓ |
| Generic behind an explicit allowlist | Generic refusal bounded to an enumerated command set, so no other family changes. | |

**User's choice:** Generic — fix the whole class now.
**Notes:** Surfaced before asking: `op_execute_stateful_operation` returns `false` at `operation_utils.cpp:89` when `main` is NULL, so the caller reports finished with `response_code == OK` and no error — DEVTEST-01's phantom-erase mechanism. Consequences accepted knowingly: Phase 121's scope and the REQUIREMENTS mapping must be amended in-phase, and a full cross-family trace/regression sweep is required.

---

## Lock table + the frozen shared header

### Q1 — Where the SDP-enable table comes from

| Option | Description | Selected |
|--------|-------------|----------|
| Local `EEPROM_SDP_ENABLE[3]` + cross-guard | Mirror 117 D-10; `flash_utils.h` stays byte-frozen; guard pins it against `FLASH_ENABLE_WRITE_PROTECTION`. | ✓ |
| Drive `FLASH_ENABLE_WRITE_PROTECTION` directly | Give the zero-caller table its first caller; zero duplication, but couples `0x0D` to a shared frozen header. | |
| Local table, no cross-guard | Comment only; cheapest, but nothing catches divergence. | |

**User's choice:** Local `EEPROM_SDP_ENABLE[3]` + cross-guard.

### Q2 — Discharging LOCK-05 given the dual-purpose hazard

| Option | Description | Selected |
|--------|-------------|----------|
| Three-way guard + no-payload trace assertion | Guard asserts three-way byte identity and three distinct objects; native case asserts the stream ends after exactly 3 writes. | ✓ |
| Guard + comment, no stream-length assertion | Trust the golden's full-stream equality to catch a stray data write implicitly. | |
| Comment only, next to the local table | LOCK-05's letter, satisfied with prose. | |

**User's choice:** Three-way guard + no-payload trace assertion.
**Notes:** Surfaced during the question: `AA-55-A0` is byte-identical to `FLASH_ENABLE_WRITE`, the protected-write prefix — so lock-vs-write is discriminated only by the *absence* of a following data write. Strictly worse than FIX-05's one-nibble hazard, and an absence has to be asserted on the stream, not on a table.

### Q3 — Where the lock goldens live

| Option | Description | Selected |
|--------|-------------|----------|
| Extend `sdp_expected.h`, prove per-array | One home for `0x0D` goldens; identity proof shifts from whole-file SHA to per-array byte-identity. | ✓ |
| New separate lock-goldens header | Keeps `sdp_expected.h`'s whole-file blob-SHA shorthand intact. | |
| In-suite literals, no shared header | Zero shared-file churn; breaks the `_shared/` pattern. | |

**User's choice:** Extend `sdp_expected.h`, prove per-array.
**Notes:** The whole-file blob-SHA shorthand 117/118 used for this file no longer applies after this phase — must be stated explicitly.

### Q4 — Where the lock proof lives, and how wide

| Option | Description | Selected |
|--------|-------------|----------|
| Split by existing home, all four pinouts | Production stream + three-way distinctness in `test_eeprom28c_sdp`; table cross-guard in `test_sdp_harness`; lock pinned on all four `0x0D` pinouts. | ✓ |
| Split by home, one representative pinout | Same split, one pinout; smaller diff, but the remap is proven for a 6-write sequence, not a 3-write one. | |
| All in `test_eeprom28c_sdp`, all four pinouts | One suite owns everything; the cross-guard drifts from its 117-04 sibling. | |

**User's choice:** Split by existing home, all four pinouts.

---

## What a standalone lock reports

### Q1 — What OK means, and how it is worded

| Option | Description | Selected |
|--------|-------------|----------|
| OK = sequence emitted, said in words | `response_code` untouched; the report line states the sequence was emitted and that state cannot be read back. | ✓ |
| OK + an explicit unverifiable WARN | Loudest, but warns on a correctly completed operation — the shape 118 D-02 rejected. | |
| Report the DQ6 poll's outcome | Real but misleading evidence — the inverted-read-back mistake FIX-02 deleted, in a new costume. | |

**User's choice:** OK = sequence emitted, said in words.
**Notes:** Puts HOST-05's no-fabricated-boolean guarantee in the firmware, not only in Phase 120's CLI.

### Q2 — What happens after the lock's 3 writes

| Option | Description | Selected |
|--------|-------------|----------|
| `t_WC` delay only | LOCK-01's literal shape; stream is exactly 3 writes; goldens stay free of read-induced `CONTROL` churn. | ✓ |
| Reuse the full completion function | Symmetry with the unlock; injects ~33 reads into all four lock goldens for an outcome never reported. | |
| `t_WC` + a lock-specific silent poll | A third timing shape in a file that already has two. | |

**User's choice:** `t_WC` delay only.

### Q3 — Catalog ids

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse for unlock, new pair for lock | Standalone unlock emits 118's `0x5E`/`0x5F`; lock gets its own emitted + duration pair. Two new ids. | ✓ |
| New distinct ids for all four | The log says *why* the sequence ran; four new ids, more catalog surface. | |
| Reuse for unlock, one line for lock | One new id, cheapest; the lock then has no duration report. | |

**User's choice:** Reuse for unlock, new pair for lock.

### Q4 — Does the lock get the bracket and budget check

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — shared helper for both | 118's budget is already length-parameterised, so factoring the bracket + check into one helper is nearly free. | ✓ |
| No — the shared emitter already covers it | A user who only ever locks never exercises the check, and the lock's line carries no number. | |
| Bracket yes, runtime check no | The "nothing fails when the budget is blown" shape 118 D-09 rejected. | |

**User's choice:** Yes — shared helper for both.
**Notes:** At n=3 the budget is 300 µs and F-118-01's ~95 µs/byte lands near ~286 µs — the same ~4.7 % margin as at n=6.

---

## LOCK-06 headroom + page-load measurement

### Q1 — How LOCK-06 is judged

| Option | Description | Selected |
|--------|-------------|----------|
| Judge against 2992 B, restate in-phase | Measure against the live `25680/28672`; record `3348 B` as a superseded pre-117 figure with the arithmetic shown. | ✓ |
| Keep 3348 B as a cumulative milestone budget | Report v1.22's running total; LOCK-06 then can't be judged from this phase's artifacts alone. | |
| Report both framings | Nothing lost, but two budgets to reconcile and a later reader may quote the flattering one. | |

**User's choice:** Judge against 2992 B, restate in-phase.
**Notes:** Correction goes in CONTEXT and the SUMMARY; REQUIREMENTS.md is not edited.

### Q2 — The page-load timing measurement

| Option | Description | Selected |
|--------|-------------|----------|
| Take it — worst-case, reported once | Bracket the per-byte loop, track the worst interval, report one line after the write completes. | ✓ |
| Take it, and make it a runtime check too | Fully reverses 118 D-10; adds a compare to the hot per-byte path. | |
| Defer, and record the declination | Name the flash-vs-timing conflation and hand the measurement to a future gh#11 phase. | |

**User's choice:** Take it — worst-case, reported once.
**Notes:** A naive per-page bracket would emit ~512 lines on a 32 KB write. PROJECT.md's FIFTH CORRECTION item 3 directs this measurement at LOCK-06 while conflating a flash budget with a timing one — say so, then answer the timing question anyway.

### Q3 — Bench scope

| Option | Description | Selected |
|--------|-------------|----------|
| Page-load now, lock duration in 120 | Only the shipped CLI (`write -b --force`) drives the bench, so firmware-before-host holds in practice. | ✓ |
| Add a throwaway raw-frame script | Gets all three numbers now; exercises a new state-mutating command via an unreviewed instrument. | |
| Native only — no bench run | Zero bench risk; forfeits the answer to an explicit PROJECT.md directive. | |

**User's choice:** Page-load now, lock duration in 120.
**Notes:** `CMD_SDP_LOCK` is unreachable without Phase 120's `dev sdp` command.

### Q4 — Bench setup

| Option | Description | Selected |
|--------|-------------|----------|
| Same as 118 — autonomous, empty socket | Leonardo connected, socket empty, `autonomous: true`, `controller:` identity verified per port. | ✓ (extended) |
| Autonomous, but a chip is seated now | Scope the run so `write -b --force` cannot damage a seated part. | |
| Checkpoint before touching hardware | Operator confirms board and socket state before any port opens. | |
| Bench not available — plan for native only | Record the margin as not-measured with the reason. | |

**User's choice (free text):** *"Same as 118 and test uno and uno328pb that is also connected."*
**Notes:** Reverses 118's D-12 Leonardo-only scope — **all three** boards are measured. Worth it because F-118-01's 4.7 % margin may not be board-invariant (ATmega32u4 vs ATmega328P/PB register paths, 512 vs 1024 byte buffer). Recorded as a reversal *with* its constraints, so it is not read as the new default.

### Q5 — Socket state on the Uno-class boards

| Option | Description | Selected |
|--------|-------------|----------|
| All three sockets empty | Fully autonomous; uploads to all three with no checkpoint anywhere. | ✓ |
| Chips seated on the Uno-class boards | Insert a pull-the-chip checkpoint before each Uno-class upload. | |
| Leonardo empty, Uno-class unknown | Checkpoint before each Uno-class upload only. | |

**User's choice:** All three sockets empty.
**Notes:** Asked because sideloading firmware to a Uno-class board drives the shield bus (Leonardo exempt) — `.planning` memory `feedback_chip_out_before_sideload.md`. The plan must state that the rule is satisfied by this statement rather than silently skipping it. Standing uno328pb cautions still apply: bench-instability (retry on timeout, never trust N=1), the VPP-recal/brownout history (should not apply to a 5 V protocol — state the reasoning), and that it is really a plain Uno with mismatched firmware.

---

## Claude's Discretion

- Whether lock and unlock share one op-layer function or take two.
- Exact format strings, wording and id numbers for the two new lock catalog entries (names ≤32 chars).
- Where `is_memory_cmd()` is declared, and whether it also gates `loop()`'s switch.
- The shared bracket helper's signature; whether the page-load worst-case tracker is file-static or handle-threaded.
- Whether `[env:native_nodevtools]` runs the full `test_filter` or a subset (the truth-table suite is mandatory in both).
- Whether `configure_eeprom28c` gets any narrowly-scoped `default:` arm at all.
- Plan ordering, subject to catalog-before-call-sites and LOCK-03-before-LOCK-02.

## Deferred Ideas

- `prove-pio-dev-flag-fails-closed.md` items 1–3 — the `${sysenv.*}` gating matrix; stays with 999.15 / gh#8.
- A per-byte runtime t_BLC WARN on the page-load loop — measured and reported here, not checked.
- A distinct "compiled out" refusal id for `CMD_DEV_*` in a release build.
- A pre-dispatch `protocol != 0x0D` check in `configure_memory`; `default:` arms in all six handlers.
- A throwaway raw-frame bench script emitting `cmd: 9`/`cmd: 10`.
- Four distinct catalog ids distinguishing auto-unlock from standalone unlock.
- Deleting the host's `_SRAM_PROTO_IDS` workaround if D-07 makes it dead code — identify here, act in Phase 120.
- Carried forward: the declined trace-recorder widening (third strobe kind); the `infoic.xml` `page_size` decode phase; Unity-teardown SIGABRT; SDP-F7; SDP-F8.
- Reviewed but not folded: `fold-response-code-into-log-macro.md` (conflicts with 117 D-05 / 118 D-02 / this phase's D-12); `decode-infoic-flags-bits-14-15-protect-metadata.md` (host/DB work; HOST-04 requires zero DB change).
