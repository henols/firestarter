# Phase 119 Non-Regression Sweep — the enumerated command-by-protocol exception record

**Written:** 2026-07-28 (Plan 119-10)
**Firmware phase base:** `1880054` (`firestarter`, Phase 118's own sweep HEAD) · **Host phase base:** `d3f9128` (`firestarter_app`, Phase 118's own sweep HEAD) · **Meta phase base:** `4c286b3` (`.planning`, Phase 118 PROJECT.md evolution commit)
**Firmware HEAD at this sweep:** `0048b3d` · **Host HEAD at this sweep:** `9ead17f`

This is the single artifact a later reader should open to answer "what did Phase 119 change,
and what did it prove unchanged". It aggregates and re-derives (never merely copies) the claims
made in `119-01`..`119-09`'s SUMMARYs, executes the full three-repo non-regression sweep at the
phase's final code state, and closes **LOCK-06** — the last open LOCK requirement.

---

## 1. The claim, stated precisely

Phase 119 added the milestone's only new state-mutating operation (`CMD_SDP_LOCK`) and one
generic refusal (`operation_utils.cpp`'s NULL-`main` guard) that changes observable behaviour
across **every** protocol family, not just `0x0D`. So the claim here is not "nothing changed" —
that would be false. The claim is three precise statements, and anything not covered by them is
unchanged:

1. **The recorded BUS streams for `0x05`, `0x06`, `0x07`, `0x08`, `0x0B`, `0x10` and SRAM are
   byte-identical** to the phase base. No golden for any of those five `test_val_*` families was
   regenerated (§3).
2. **The serial channel gained a bounded, enumerated set of new frames** — three new INFO ids
   introduced this phase (`0x60`, `0x61`, `0x62`) plus the pre-existing `MSG_ERR_NOT_SUPPORTED`
   (`0xA5`) now reachable on paths that previously emitted nothing at all (§2).
3. **One class of previously-silent outcomes became explicit refusals, enumerated cell by
   cell** — every command × protocol combination whose handler leaves `firestarter_operation_main`
   NULL now reports `MSG_ERR_NOT_SUPPORTED` instead of a silent `RESPONSE_CODE_OK` (§2's second
   table).

Everything else — the `0x0D` bus stream's own shape for `read`/`write`/`verify`, every other
protocol's dispatch order, the catalog codegen ritual, the DB — is unchanged, and this document
proves that rather than asserting it.

---

## 2. The enumerated exceptions, in two tables

### Table A — every new or newly-reachable serial frame this phase can emit

| Id | Hex | Path | Condition | Landed in |
|----|-----|------|-----------|-----------|
| `MSG_INFO_SDP_LOCK` | `0x60` | `CMD_SDP_LOCK` (standalone or future host callers) | Unconditional, emitted before the 3-write enable sequence | Plan 119-01 (catalog), Plan 119-04 (emitter) |
| `MSG_INFO_SDP_LOCK_DONE_US` | `0x61` | `CMD_SDP_LOCK` | Unconditional, emitted after the sequence; carries the `micros()`-measured emit duration and states in its format string that protection state is not readable (D-12) | Plan 119-01 (catalog), Plan 119-04 (emitter) |
| `MSG_INFO_PAGE_LOAD_WORST_US` | `0x62` | `eeprom28c_write_execute`'s per-byte page-load loop | Unconditional, emitted exactly once per write, on **both** the completing and the aborting exit (single-exit restructure) | Plan 119-01 (catalog), Plan 119-08 (tracker + emitter) |
| `MSG_ERR_NOT_SUPPORTED` | `0xA5` | `operation_utils.cpp`'s NULL-`main` fall-through, `op_execute_stateful_operation` | Fires for `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK` on every protocol other than `0x0D`; for `CMD_ERASE`/`CMD_CHECK_CHIP_ID` on `0x0D`; and for the newly-refused SRAM cells (Table B) — reusing the pre-existing id (already `eprom_erase`'s `FLAG_CAN_ERASE` refusal), no new catalog entry | Plan 119-07 (the generic guard) |

On any of these paths, exactly the frames named above are added — no other id, no silent
behaviour change to any existing id's format string or severity band.

### Table B — the complete command-by-protocol matrix (LOCK-04's positive invariant, LOCK-02's dispatch half, DEVTEST-01's firmware-half gaps)

Restated from Plan 119-07's SUMMARY (its Task 3 produced this; this document re-verifies it still
holds at the phase's final commit and does not re-derive it). `G` = generic pre-set main
(`memory.cpp:48-58`), `H` = handler-specific main, `NULL→refused` = this phase's new
`MSG_ERR_NOT_SUPPORTED` refusal (was a silent `∅`/OK before this phase), `unchanged` =
`configure_not_implemented`'s own earlier `RESPONSE_CODE_ERROR`, never touching the op layer at
all.

| Protocol(s) | Handler | READ (1) | WRITE (2) | ERASE (3) | BLANK_CHECK (4) | CHIP_ID (5) | VERIFY (6) | SDP_UNLOCK (9) | SDP_LOCK (10) |
|---|---|---|---|---|---|---|---|---|---|
| `0x07 0x08 0x0B` | `configure_eprom` | G | H | H | H | H | G | **NULL→refused** | **NULL→refused** |
| **`0x0D`** | `configure_eeprom28c` | G | H | **NULL→refused ⚠ DEVTEST-01 fw half** | H | **NULL→refused (upstream-gated, see below)** | G | **H (new, LOCK-02)** | **H (new, LOCK-02)** |
| `0x10` | `configure_flash_intel` | G | H | H | H | H | G | **NULL→refused** | **NULL→refused** |
| `0x06` | `configure_flash_nor_unlock` | G | H | H | H | H | G | **NULL→refused** | **NULL→refused** |
| `0x05 0x35 0x39` | `configure_flash_5v_page` | G | H | H | H | H | G | **NULL→refused** | **NULL→refused** |
| `0x0E 0x27 0x28 0x29` | `configure_sram` (empty body) | G | G | **NULL→refused** | **NULL→refused (see below)** | **NULL→refused (upstream-gated)** | G | **NULL→refused** | **NULL→refused** |
| `0x11 0x2A-0x2C 0x34 0` | `configure_not_implemented` | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged |

**Cells with a qualification, stated honestly, not over-claimed:**

- **`0x0D` + `CMD_CHECK_CHIP_ID`** and **SRAM + `CMD_CHECK_CHIP_ID`**: also newly refused by this
  guard, but `eprom_check_chip_id` already refuses earlier with `MSG_ERR_NO_CHIP_ID` when
  `handle->chip_id == 0`, and TRACE-05 pinned `chip_id_check: false` across all 84
  `algorithm == 13` entries — so in practice the host never sends a non-zero chip id for `0x0D`,
  and this cell is already refused **upstream** of this guard. This guard is not the primary
  mitigation for that cell.
- **SRAM + `CMD_BLANK_CHECK`**: also newly refused at this guard, but the host's
  `_SRAM_PROTO_IDS` workaround in `firestarter_app/firestarter/eprom_operations.py`
  short-circuits `check_eprom_blank` **before any firmware command is issued**, so this guard is
  not reachable from that call path today. It does **not** become dead code — it fires earlier
  and gives a materially better user-facing message. Correct Phase 120 disposition: **keep, not
  delete** (RESEARCH F-F2). `firestarter_app` was not modified by this claim's own mechanism.
- **`0x0D` / SRAM + `SDP_UNLOCK` / `SDP_LOCK`**: this is where D-06's "provably total" claim earns
  its keep — every non-`0x0D` protocol family is refused by the **same one guard**, with no
  per-handler maintenance, which is exactly LOCK-04's fail-closed intent (not its literal
  `default:`-arm mechanism, which D-05 disproved — see §7).

**Cross-family byte-identity confirmed, not assumed, in this sweep:** `test_val_eprom`,
`test_val_nor_unlock`, `test_val_5v_page`, `test_val_flash_intel` and `test_val_sram` are all
green with **no golden regenerated** — the matrix above shows why: no cell any of those five
stream suites exercises changes from `G`/`H` to anything else; the change is purely in the
`NULL→refused` cells, none of which emitted bus traffic before this phase.

**Pre-existing test cases whose expectation moved — the honest answer is zero.** Re-verified from
Plan 119-07's own record: no native suite drove the op layer with a NULL `main` before Task 1 of
that plan widened both native envs' `build_src_filter` to link `operation_utils.cpp` — so there
was no pre-existing case anywhere in the 17-suite tree that encoded the old silent-OK expectation
for any of these newly-refused cells, and therefore no case had to be edited or re-asserted. The
new refusal behaviour is proven exclusively by **new** cases (case groups 1-6 in
`test_configure_memory.cpp`, cases 24/25 in `test_eeprom28c_sdp.cpp`), never by flipping an old
one.

---

## 3. Why the bus stream is genuinely unchanged

The structural argument, re-verified rather than trusted: no cell in any column the other six
families exercise (`READ`, `WRITE`, `VERIFY` for every protocol; every command for `0x0D` other
than the two new ones and the three newly-refused ones) changed from `G`/`H` to anything else.
The entire change is confined to previously-**NULL** cells, none of which ever emitted bus
traffic — a NULL `main` never called `firestarter_set_data`/`firestarter_get_data` before this
phase either; it just returned `false` silently. Making that path **log** something touches the
serial channel, never the recorded strobe stream.

**The five `test_val_*` stream suites are green with no golden regenerated** (re-confirmed this
sweep: `pio test -e native -f "*test_val_*"` passes as part of the full 141/141 run, and none of
`test_val_eprom`, `test_val_nor_unlock`, `test_val_5v_page`, `test_val_flash_intel`,
`test_val_sram`'s golden expected-arrays were touched in the phase's diff — confirmed by the
real-path enumeration in §4).

**Golden blob-SHA identity, re-derived in this sweep (not copied from any prior plan's SUMMARY):**

```
$ cd /workspaces/firestarter && for p in test/native/avr/_shared/sdp_expected.h test/native/avr/_shared/host_stubs_common.inc test/native/avr/_shared/sdp_bus_config.h; do echo "$p base=$(git rev-parse 1880054:$p) head=$(git rev-parse HEAD:$p)"; done
test/native/avr/_shared/sdp_expected.h base=b0566b80a360261cf825df5f23ecc05c7d0f885e head=dd1ba1cce60d8aa8934e8c067ed82ad85cfd3b83
test/native/avr/_shared/host_stubs_common.inc base=675166d3e5383d9ca7afa7911afbaa41b93f52da head=0858caf419c6170fb0e54c636ae273256910b3d9
test/native/avr/_shared/sdp_bus_config.h base=e0111e6452dcb1bd8f44c5d36f3f6a67b893f4ad head=e0111e6452dcb1bd8f44c5d36f3f6a67b893f4ad
```

Three different results, all expected, none silent:

- **`sdp_bus_config.h` is blob-SHA identical.** Kept whole-file shorthand — matches phase base
  exactly, zero regeneration, confirmed by `gen_sdp_bus_config.py --check` in this sweep (§5 row
  4) matching a fresh regeneration byte-for-byte.
- **`sdp_expected.h`'s whole-file blob SHA necessarily changed.** D-10 forces this: Plan 119-05
  added four new `SDP_FIXED_LOCK_*` arrays. **Phases 117 and 118's whole-file blob-SHA identity
  shorthand does NOT apply to this file any longer, for this phase or any future one that touches
  it.** The replacement proof is Plan 119-05's per-array byte-identity of the *pre-existing*
  arrays, re-verified in this sweep by diffing the current file against the phase-base blob and
  confirming the diff is additions-only:
  ```
  $ git diff 1880054..HEAD -- test/native/avr/_shared/sdp_expected.h | grep '^-' | grep -v '^---' | wc -l
  0
  ```
  Zero removed lines — every pre-existing `SDP_SHIPPED_*`/`SDP_FIXED_*` array is untouched,
  byte-for-byte. This method and result are restated here (Plan 119-05 first established them,
  Plan 119-08 re-confirmed them); this sweep re-ran the diff itself rather than trusting either
  prior record.
- **`host_stubs_common.inc` is NOT blob-identical, and that is a correction handed forward from
  Plan 119-08, re-confirmed here.** Plan 119-07 Task 1 added one no-op
  `extern "C" void op_reset_timeout() {}` stub when it widened both native envs'
  `build_src_filter` to link `operation_utils.cpp` (that TU calls `op_reset_timeout()`
  unconditionally, and the AVR-only definition in `firestarter.cpp` is outside both native
  envs' filter). Re-confirmed additions-only in this sweep:
  ```
  $ git diff 1880054..HEAD -- test/native/avr/_shared/host_stubs_common.inc
  (14-line addition, one no-op stub function + its provenance comment; zero pre-existing lines touched)
  ```
  This file **keeps the blob-SHA shorthand as a concept** (it is still meaningful to ask "is this
  file identical" — the answer this phase is simply "no, and here is the one, additions-only,
  reason"), unlike `sdp_expected.h` whose shorthand is retired outright because D-10 makes a
  whole-file-identical answer structurally impossible for that file going forward.

---

## 4. Flash and RAM

### Part 1 — the measured figures with provenance

Phase base: firmware commit `1880054` (Phase 118's own sweep HEAD). Final: firmware commit
`0048b3d` (this sweep's HEAD, Plan 119-08's last code commit).

| Board | Base (`1880054`) | Final (`0048b3d`) | Flash Δ | RAM (base → final) |
|---|---|---|---|---|
| Leonardo | Flash 25680/28672 | Flash **26072**/28672 | **+392 B** | 1998/2560 → 2014/2560 (+16 B) |
| Uno | Flash 23542/32256 | Flash **23932**/32256 | **+390 B** | 1559/2048 → 1573/2048 (+14 B) |
| uno328pb | Flash 23592/32384 | Flash **23976**/32384 | **+384 B** | 1563/2048 → 1579/2048 (+16 B) |

Re-measured in this sweep, not copied: `pio run` (all three AVR envs) — **3/3 SUCCESS**, figures
exactly as shown above, matching Plan 119-08's own ending measurement byte-for-byte.

**Uno and uno328pb capacities differ (32256 versus 32384) because the two board JSONs reserve
different bootloader sizes**, so any cross-board comparison in this document compares **deltas
only** — never free-space figures, never percentages. Phase 118 reported two boards (Leonardo,
Uno); this phase reports **three**, per D-18 item 5 (uno328pb added).

### Part 2 — D-15's arithmetic, shown

LOCK-06's requirement text (`REQUIREMENTS.md`, pre-this-plan wording) cites **3348 B** of
headroom. That figure is a **pre-Phase-117 measurement, now superseded**: Phase 117 measured
`+204 B` and Phase 118 measured `+152 B` (both against Leonardo), and both are already spent —
that is exactly the difference between `3348 B` and the live figure.

The live Leonardo headroom at **this phase's own base** (`1880054`, i.e. after Phases 117 and 118
have already been paid for) is:

```
28672 (Leonardo flash capacity) − 25680 (flash used at phase base) = 2992 B
```

**This phase's delta is judged against 2992 B, not against 3348 B.** This phase's own measured
Leonardo delta is **+392 B** (Part 1 above), so:

```
2992 B (live headroom at phase base) − 392 B (this phase's measured delta) = 2600 B free remaining
```

Cross-checked directly against the final measurement: `28672 − 26072 = 2600 B` — the two
arithmetic routes agree.

**No threshold claim beyond "fits" is made anywhere in this document.** No percentage-of-headroom
framing, no "plenty of room" framing, and explicitly not a cumulative-milestone-budget framing —
D-15 rejected treating `3348 B` as a whole-milestone budget precisely because LOCK-06 must be
judgeable from this phase's own artifacts alone, not from a running total across 117/118/119.
Reporting both the "fits against 2992 B" framing and a cumulative-budget framing side by side was
also considered and rejected (D-15): it would invite a later reader to quote whichever framing is
more flattering. This document states one framing, with its arithmetic shown, and stops there.

**The `-D DEV_TOOLS` configuration is the tighter one and therefore the binding constraint for
LOCK-06.** A release-config (`-D DEV_TOOLS` absent) Leonardo build measured **24388/28672** at
this phase's base (RESEARCH's temporary `[env:leonardo_nodevtools]` experiment, `platformio.ini`
restored byte-clean afterward, `git status --short` confirmed empty) — so the flag itself costs
`25680 − 24388 = 1292 B`. Since `-D DEV_TOOLS` costs flash rather than saving it, the `DEV_TOOLS`
build carries the **smaller** headroom of the two configurations and is the one this document's
delta is reported against (2600 B free, not an inferred, larger, unmeasured release-config
figure). This phase did not re-run a temporary release-config build with the full `+392 B` delta
applied — the 1292 B figure is restated from RESEARCH's own measurement (as Plan 119-08 and
119-09 also restated it, consistently), not re-derived in this sweep.

### Part 3 — the decomposition, attributed per plan

Re-verified against each plan's own recorded figures (not re-derived from scratch):

| Plan | What it added | Leonardo Δ | Uno Δ | uno328pb Δ | Leonardo running total |
|---|---|---|---|---|---|
| 119-01 | Three catalog ids — numeric `#define`s only, no PROGMEM string table referencing them yet | +0 B | +0 B | +0 B | 25680 |
| 119-02 | `is_memory_cmd()` (static inline, eight-case switch) + `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK` defines + restructured `if`/`else` in `parse_json`; the second native env costs 0 B on the AVR builds (native-test-only). Predicate is `static inline`, so its cost lands at its one call site. | +12 B | +12 B | +12 B | 25692 |
| 119-04 | `EEPROM_SDP_ENABLE[3]` + rationale comment; `eeprom28c_emit_sdp_sequence_timed()` shared helper (de-duplicates part of 118's inline bracket, so its own net contribution may be neutral-to-negative on its own — the +262 B reported here is the combined cost of the table, the helper, both standalone ops, both entry points and both `configure_eeprom28c`/`loop()` switch arms, not the helper alone) | +262 B | +260 B | +254 B | 25954 |
| 119-05 | Test-only (four dump-authored goldens, scripted `micros()` queue, cases 13-19) | +0 B | +0 B | +0 B | 25954 |
| 119-06 | Test-only (three-way identity/distinctness guard, cases 20-23, host parity leg) | +0 B | +0 B | +0 B | 25954 |
| 119-07 | Generic NULL-`main` refusal at the op layer (one `LOG_ERROR_ID` call + a `response_code` store); `+<operation_utils.cpp>` widening itself costs 0 B on the AVR builds (native-only filter change) | +18 B | +18 B | +18 B | 25972 |
| 119-08 | Worst-per-byte page-load tracker + single-exit restructure + one `LOG_ID_U32` report call | +100 B | +100 B | +100 B | **26072** |
| 119-09 | Meta-only (ROADMAP/REQUIREMENTS/PROJECT.md/STATE.md/todo) — 0 B, no firmware touched | +0 B | +0 B | +0 B | 26072 |
| **Total phase delta** | | **+392 B** | **+390 B** | **+384 B** | |

**No residual to force.** Every plan's own attributed figure sums exactly to the measured total
delta on all three boards (`12+262+18+100 = 392` for Leonardo; the same four non-zero plans sum
to `390` for Uno and `384` for uno328pb, matching the measured per-plan deltas each plan's own
SUMMARY recorded) — there is no unattributed compiler-layout residual to report honestly this
time; the sums reconcile exactly.

**Zero-flash items, named so a reader does not look for their contribution in the delta above:**
the second native env (`[env:native_nodevtools]`) itself; the four `SDP_FIXED_LOCK_*` goldens;
the entire `test_cmd_admission` suite; every host-side (`firestarter_app`) artefact (catalog
regeneration, the new source-scan gate, its fixture, its pytest); and, under Plan 119-07's chosen
option (a), the widened `build_src_filter` itself (native-only, costs 0 B on any AVR env).

**This plan (119-10) itself spends 0 B** — it is meta-only, no firmware or host source file was
touched (confirmed: both submodules' working trees clean at the start and end of this plan's
work, per the repo mechanics constraint).

**LOCK-06 is marked Complete in `.planning/REQUIREMENTS.md`** with a parenthetical giving the
measured Leonardo delta (`+392 B`), the `2992 B` live headroom it was judged against, and the
note that the requirement's `3348 B` figure is superseded. **LOCK-06's own wording was not
edited.** LOCK-01 through LOCK-05 were re-confirmed already Complete before this edit; DEVTEST-01
was re-confirmed still Pending; no other requirement row was touched by this plan (`git diff
.planning/REQUIREMENTS.md` shows exactly two changed lines: LOCK-06's checkbox/parenthetical and
its traceability-table row).

---

## 5. The CORRECTION-4 item-4 gate table — now nine rows

**Why this check exists.** Phase 117 shipped a commit claiming zero `firestarter_app` files
changed while four host gates that scan firmware source text were actually broken — the firmware
suite stayed green throughout, and only the phase's own regression gate caught it (PROJECT.md's
FOURTH CORRECTION, item 4). Every phase from 118 on must include an explicit task checking
firmware renames/deletions against these gates. This phase's firmware edits touch
`include/firestarter.h`, `src/firestarter.cpp`, `src/operation_utils.cpp` and
`src/proms/eeprom_28c.cpp` — several of the exact files these gates scan — so this table is not a
formality, and it **grows from eight rows to nine**: Plan 119-03 shipped a brand-new
firmware-source-scanning gate this phase, `check_is_memory_cmd_no_ifdef.py`.

**This table is the checklist Phases 120, 121 and 122 inherit.** All nine rows executed in this
sweep, from `/workspaces/firestarter_app` unless noted:

| # | Gate | Command | Verdict |
|---|------|---------|---------|
| 1 | `tools/check_no_log_in_sdp_window.py` (repaired by Plan 119-04 after the D-14 helper refactor — HIGH-risk row) | `python3 tools/check_no_log_in_sdp_window.py` | **PASS** — `PASS: no logging call in SDP timing window (…/eeprom_28c.cpp, emitter lines 298-314, completion-poll lines 348-361)`, exit 0. The appended `_EMIT_ANCHOR_PATTERNS` entry (Plan 119-04) is append-only, per contract — both prior entries kept, unreordered. Two tripwires remain live and are named here so a future editor does not trip them unknowingly: (a) `_func_def_pattern` hardcodes a literal `void` return type, so any refactor of the emitter or completion-poll signature away from `void` breaks the gate's own definition-matcher, not just its anchors; (b) the completion-poll window's resolution depends on `eeprom28c_wait_for_sdp_completion` continuing to exist as a named function — deleting or renaming it without updating `_WAIT_ANCHOR_PATTERNS` fails the gate closed (an `ERROR:`, not a silent pass), which is correct behaviour but worth naming explicitly. **The helper's own body (`eeprom28c_emit_sdp_sequence_timed`) must never become a third scanned window** — it deliberately sits *around* the two windows, not inside either, and it carries `LOG_ID`/`LOG_ID_U32` calls by design (that is the report line itself), which would trip the gate if it were ever folded into a scanned span. |
| 2 | `tests/test_check_no_log_in_sdp_window.py` | `python3 -m pytest tests/test_check_no_log_in_sdp_window.py -q` | **PASS** — 7 passed |
| 3 | `tests/test_sdp_table_parity.py` (MEDIUM-risk row; broken 3× by Phase 117; `EEPROM_SDP_ENABLE[3]` added this phase is exactly the change class that breaks it, per Plan 119-04's own note) | `python3 -m pytest tests/test_sdp_table_parity.py -q` | **PASS** — 5 passed (was 4/4 before Plan 119-06's added parity leg) |
| 4 | **`tools/check_is_memory_cmd_no_ifdef.py` + `tests/test_check_is_memory_cmd_no_ifdef.py` + `tests/fixtures/planted_ifdef_in_predicate.h` — NEW this phase (Plan 119-03), the table's ninth row.** Scans `firestarter/include/firestarter.h`'s `is_memory_cmd()` predicate body, brace-matched; asserts (a) zero preprocessor conditionals of any kind inside the body and (b) the body's `CMD_*` set equals the frozen eight-name expected set exactly. | `python3 tools/check_is_memory_cmd_no_ifdef.py` then `python3 -m pytest tests/test_check_is_memory_cmd_no_ifdef.py -q` | **PASS** — `PASS: is_memory_cmd() has no preprocessor conditional and enumerates exactly the eight expected commands (…/firestarter/include/firestarter.h, predicate body lines 109-123)`, exit 0; pytest 6 passed (planted-fixture case, out-of-body control, comment-not-a-violation control, wrong-command-set case, two fail-closed sub-assertions) |
| 5 | `tools/gen_sdp_bus_config.py` (generator) | `python3 tools/gen_sdp_bus_config.py` | **PASS** — `OK: wrote …/_shared/sdp_bus_config.h`; `git status --short` on that path in `firestarter/` empty afterward (idempotent, no drift; blob-SHA re-confirmed identical to phase base in §3) |
| 6 | `tests/test_sdp_bus_config_drift.py` | `python3 -m pytest tests/test_sdp_bus_config_drift.py -q` | **PASS** — 4 passed |
| 7 | `tests/test_revision_constants_parity.py` (8-literal `FLAG_*` block, non-exhaustive) | `python3 -m pytest tests/test_revision_constants_parity.py -q` | **PASS** — 6 passed; `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK` are deliberately NOT added to `constants.py` this phase (Phase 120 HOST-03 scope), so this gate's non-exhaustive `FLAG_*` check is unaffected either way |
| 8 | `tests/test_dispatch_mirror.py` | `python3 -m pytest tests/test_dispatch_mirror.py -q` | **PASS** — 2 passed |
| 9 | `tools/check_dispatch.py` (expected untouched by this phase) + `tools/check_devtest_orchestrator.py` (host-only files, untouched by this firmware-heavy phase) | `python3 tools/check_dispatch.py` then `python3 tools/check_devtest_orchestrator.py` | **PASS** — `check_dispatch.py`: `PASS: all 746 chips scanned; 736 supported; 10 chips confirmed non-dispatchable …; 0 dispatch regressions; 0 consistency violations`, exit 0. `check_devtest_orchestrator.py`: `PASS: scanned ../firestarter/chip_test.py, ../firestarter/cli_handlers.py, ../firestarter/submit.py; 0 VPP-set, 0 raw-wire-dict, 0 --force; firmware untouched (host-only, asserted)`, exit 0; its own pytest (`tests/test_check_devtest_orchestrator.py`, 14 passed) re-run separately, not part of the six-module combined count above |

Every row PASS. No row was accepted on the strength of an earlier plan's SUMMARY alone — each
command above was re-run in this sweep, at the phase's final commit.

**Avoiding the vacuous-path trap.** Every check above targets a real, existing tool or test file
(verified present before running); none is a bare `git diff -- <path>` against a path this phase
never touches. §4-adjacent real-path enumeration below is the explicit discipline this table's
own row 1 depends on for its own continued correctness.

**This table is the checklist Phases 120, 121 and 122 inherit — nine rows, not eight.** Row 4
(`check_is_memory_cmd_no_ifdef.py`) is this phase's addition; every future phase touching
`is_memory_cmd()`, `firestarter.h`'s admission surface, or the eight-command enumeration must
re-run it, exactly as row 1 must be re-run for any future `eeprom_28c.cpp` emitter change.

---

## 6. Known-and-explained conditions — never silent

**1. Meta `.github/workflows/catalog-sync-check.yml` is expected-red-until-milestone-merge.** It
checks out both `firestarter` and `firestarter_app` at `ref: main` (confirmed at lines 33 and 40
of the workflow file in this sweep). Because v1.22 has not merged to `main` in either sub-repo,
this workflow compares this branch's meta catalog against the pre-v1.22 sub-repo `main` copies
and **cannot go green** until the milestone merges. This is expected, not a Phase-119 (or
Phase-117/118) regression, and it is not this phase's damage.

The **actual in-phase proof**, executed in this sweep and passing:
```
$ cmp tools/catalog/messages.toml firestarter/tools/catalog/messages.toml   # exit 0
$ cmp tools/catalog/messages.toml firestarter_app/tools/catalog/messages.toml  # exit 0
$ python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check
OK: catalog valid (73 messages, version 1).   # both sub-repos, both exit 0
```
Plus regenerate-and-`git diff --exit-code` clean for both `firestarter/include/messages.h` and
`firestarter_app/firestarter/messages.py` (§4-adjacent §5 row-5-class proof, re-run in this
sweep).

**2. `firestarter/.github/workflows/build.yml`'s new `native_nodevtools` step will not fire on
this milestone branch.** Plan 119-02 added a "Run native unit tests (no DEV_TOOLS)" CI step
immediately after the existing native step. That workflow triggers on `push`/`pull_request` to
`main` only (confirmed in this sweep: `on: push: branches: [main]`), so the step is inert on
`v1.22-at28c-software-data-protection-lifecycle` until the milestone merges. This is expected,
recorded in the step's own comment, and the local `pio test -e native_nodevtools` run in this
sweep (§ header — 141/141) is the in-phase proof, not the CI job.

**3. `tests/test_audit_coverage_matrix.py::test_golden_file_matches` is pre-existing RED, not
this phase's regression.** Re-confirmed in this sweep:
```
FAILED tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches
AssertionError: regenerated matrix drifted from golden fixture; produced 186034 bytes vs golden 184631 bytes
```
A stale golden fixture, unrelated to any Phase 119 change — same failure class Phase 118's own
sweep recorded (`.planning` memory `reference_audit_coverage_matrix_golden_stale.md`). Needs a
dedicated golden regen in its own plan; not chased here.

**4. `tests/test_no_programmer_found_read`/`_erase` did NOT fail in this sweep, despite three live
boards attached.** This sweep's environment has `/dev/ttyACM0`, `/dev/ttyACM1` and `/dev/ttyUSB0`
all present (confirmed via `ls`), which is exactly the condition Phase 118's own sweep recorded as
defeating this test pair's `comports=[]` monkeypatch — yet, as in that sweep, the pair passed
(`2 passed` when run in isolation). This is an environment-conditional characterization test, not
a regression either way; the disposition is recorded here by the actual observed state (pass),
not forced to match either possible outcome (`.planning` memory
`reference_characterization_no_programmer_tests_fail_with_live_board.md`). No code in this phase
touches this test or its fixtures.

**Net, this sweep's full host run:** `python3 -m pytest --tb=no -q` → **981 passed, 1 failed**
(`test_audit_coverage_matrix`, condition 3 above). None of these four conditions is this phase's
damage; none is silent.

---

## 7. Validation ceiling

Quoted verbatim from `.planning/REQUIREMENTS.md` §"Validation Ceiling":

> **Provable in software:** the emitted address/data/strobe byte-stream is correct per pinout and
> per size band; the sequence contains no logging and its host-side duration is measured;
> lock/unlock is `0x0D`-scoped and fail-closed elsewhere; the admission guard is
> `DEV_TOOLS`-invariant; the other protocol families' traces are byte-identical; the host refuses
> before opening a port.
>
> **NOT provable without an AT28C part:** that silicon actually enters or leaves the protected
> state; that `tBLC` is met *as accepted by the die*; that gh#11's symptom is gone; that the
> curated capability partition is correct per family.
>
> **Permitted claim at close:** *"The SDP lock and unlock sequences are emitted exactly as
> specified, verified byte-exact by golden register trace across all four `0x0D` pinouts, with a
> documented and measured host-side timing assumption."*
>
> **Forbidden claim:** *"SDP lock/unlock works on an AT28C256."*

**This document sits entirely on the permitted side of that line.** Every claim above has a
recorded artifact as its subject: a register-trace strobe pinned by golden comparison (§2 Table
B, §3), a captured serial frame's id byte (§2 Table A), a git blob SHA (§3), a `pio run`
size-report line (§4), a pytest exit code (§5, §6). The lock and unlock sequences are emitted
exactly as specified, verified byte-exact by golden register trace across all four `0x0D`
pinouts (Plan 119-05's Cases 13-16), with a documented and measured host-side timing assumption
(Plan 119-06's Cases 21/22, the D-14 budget check). **Nothing in this document supports the
forbidden claim.** `0x0D` stays **`UNVERIFIED`** in the `PROTOCOL-LEDGER`. **Zero** chips changed
`support_status`. The **84**-chip count is unchanged, re-confirmed by this sweep's DB identity
check (§4-adjacent — `chip_database.json` diff against phase base is empty). This document
changes no count and touches no `PROTOCOL-LEDGER` entry.

**No bench byte in this phase could lock a real part.** `CMD_SDP_LOCK` is unreachable from the
shipped CLI: no `firestarter` host command emits `cmd: 10` on the wire today — that CLI surface
(`dev sdp`) is Phase 120's. This is not merely a scheduling convenience; it is the strongest
safety argument this phase has for the firmware-before-host ordering invariant. A firmware
capability that can enable write-protection on a real chip exists in this phase's tree, but it is
provably unreachable except through a hand-crafted raw JSON command over serial — something no
released tool does — until Phase 120 wires a reviewed CLI path to it.

---

## 8. Deliberately not taken

Recorded here so the next owner **finds** these as explicit decisions, not as inherited silence.

**1. `default:` arms in all six `configure_*` handlers.** Priced at roughly 90-130 B and
rejected (D-06). Most self-documenting, most flash, and each arm would have had to be hand-written
not to swallow the pre-set generic `read`/`write`/`verify` mains `configure_memory` establishes
before any handler runs.

**2. A pre-dispatch `protocol != 0x0D` check in `configure_memory`.** Rejected (D-06) — it would
put `0x0D`-specific capability knowledge into the generic dispatcher, exactly what v1.20's
protocol-only rebuild deliberately cleaned out.

**3. Any `default:` arm in `configure_eeprom28c` at all.** Declined (D-05/D-06) in favour of a
naming comment recording why none was added, at zero flash cost. A literal `default:` arm there
would have refused `read`/`verify` on all 84 `0x0D` chips (D-05's disproof).

**4. A runtime `t_BLC` WARN on the page-load loop.** D-16's declination, preserving Phase 118's
D-10: the worst-per-byte interval is tracked and reported once, but no `AT28C_TBLC_MAX_US`
comparison or `LOG_WARN_*` call was added to the hot per-byte loop — Case 28 (Plan 119-08) proves
this explicitly, at a scripted interval 10× over budget.

**5. A distinct "compiled out" refusal id for `CMD_DEV_*` in a release build.** More honest than
the reused `MSG_ERR_UNKNOWN_CMD`, but declined (D-01) because it pre-empts 999.15/gh#8's
channel-split design and costs a catalog decision this phase does not need.

**6. An explicit refusal arm for cmd 0 / `CMD_IDLE`.** Declined on flash grounds against the live
headroom, for a frame no shipped host path emits — `CMD_IDLE` is a firmware-internal state. The
behaviour delta (silence instead of two error frames) is recorded instead (Plan 119-02, RESEARCH
F-B2).

**7. Four distinct catalog ids so the log distinguishes auto-unlock from standalone unlock.**
D-13 reused the existing pair (`0x5E`/`0x5F`) instead — revisit if the reused pair proves
ambiguous in practice.

**8. A `cmd`-carrying variant of `MSG_ERR_NOT_SUPPORTED`.** Would need a new catalog id, which
D-06 avoids; the existing id is reused as-is.

**9. Deleting the host's `_SRAM_PROTO_IDS` workaround.** Identified this phase (RESEARCH F-F2, §2
Table B's SRAM+`CMD_BLANK_CHECK` qualification) as something D-06's generic guard makes
*potentially* redundant — but it is **not** redundant, since the host short-circuit fires first.
Correct Phase 120 disposition: **KEEP**. `firestarter_app/firestarter/eprom_operations.py` was not
touched by this phase.

**10. Widening the trace recorder to a third strobe kind (data-bus-direction).** Carried forward
from Phase 117's D-12 and Phase 118's own declination — still not taken. Nothing in LOCK-01..06
required it this phase either.

**11. The lock's own hardware duration measurement.** Unreachable until Phase 120's `dev sdp` CLI
exists (D-17) — `CMD_SDP_LOCK` cannot be driven on real hardware by any released tool this phase.

**The four mechanism-versus-intent corrections this phase produced** are recorded by reference to
`.planning/PROJECT.md`'s SIXTH CORRECTION block (Plan 119-09), not restated here: LOCK-04's
mechanism (D-05/D-06), criterion 5's relocated header comment (`flash_utils.h` stays FIX-04
byte-frozen), LOCK-06's superseded `3348 B` figure plus the binding `-D DEV_TOOLS` 1292 B cost
(D-15, this document's own §4 restates the arithmetic in full since it is this document's job),
and DEVTEST-01's early-landed firmware half (D-07/D-08, Plan 119-09's owned ROADMAP/REQUIREMENTS
amendment).

---

## Sweep summary

| Gate | Command | Result |
|---|---|---|
| Native (`native`) | `pio test -e native` | 141/141, 17 suites |
| Native (`native_nodevtools`) | `pio test -e native_nodevtools` | 141/141, 17 suites — **identical to `native`**, confirming the phase's op-layer guard is `DEV_TOOLS`-invariant like everything else on the LOCK-03 chain |
| AVR builds | `pio run` | 3/3 SUCCESS — Leonardo 26072/28672, Uno 23932/32256, uno328pb 23976/32384 |
| Six named host-gate pytest modules | `pytest tests/test_sdp_table_parity.py tests/test_check_no_log_in_sdp_window.py tests/test_check_is_memory_cmd_no_ifdef.py tests/test_sdp_bus_config_drift.py tests/test_revision_constants_parity.py tests/test_dispatch_mirror.py -q` | 30 passed (5+7+6+4+6+2) |
| `check_devtest_orchestrator.py` + its pytest | `python3 tools/check_devtest_orchestrator.py` + `pytest tests/test_check_devtest_orchestrator.py -q` | PASS, exit 0; 14 passed |
| Full host pytest | `python3 -m pytest --tb=no -q` | 981 passed, 1 failed (pre-existing, §6.3) |
| `check_no_log_in_sdp_window.py` | `python3 tools/check_no_log_in_sdp_window.py` | PASS (emitter 298-314, poll 348-361), exit 0 |
| `check_is_memory_cmd_no_ifdef.py` (NEW) | `python3 tools/check_is_memory_cmd_no_ifdef.py` | PASS (predicate body lines 109-123), exit 0 |
| `check_dispatch.py` | `python3 tools/check_dispatch.py` | PASS (746 scanned, 0 regressions), exit 0 |
| `gen_sdp_bus_config.py` | `python3 tools/gen_sdp_bus_config.py` | OK, no drift |
| Catalog three-way `cmp` | `cmp` × 2 | both exit 0 |
| `codegen.py --check` | both sub-repos | both `OK: catalog valid (73 messages, version 1)`, exit 0 |
| DB identity | `git diff --stat -- firestarter/data/chip_database.json` | empty since Phase 118's own base (`d3f9128`) |
| ruff check / format | `ruff check .` / `ruff format --check .` (py3.9 target, 3.12.13 runtime) | 4 pre-existing findings (`.github/scripts/update_version.py`, `tools/catalog/codegen.py`, `tools/catalog/codegen_vectors.py`, `tools/check_mypy_watermark.py`) — identical to Phase 118's own recorded baseline, none in this phase's diff |
| Real-path diffs | `git diff --name-only` × 3 repos | captured in §4/§2; `include/flash_utils.h`, `src/proms/flash_5v_page.cpp`, `src/proms/flash_nor_unlock.cpp` all absent from the firmware list |
| Golden identity | blob-SHA + per-array diff | `sdp_bus_config.h` identical; `sdp_expected.h` additions-only (per-array proof); `host_stubs_common.inc` additions-only (14-line stub, NOT identical — correction handed forward and re-confirmed) |
| Both sub-repo working trees | `git status --short` | clean (aside from `firestarter_app`'s pre-existing, unrelated untracked files carried since Plan 119-01) |

**LOCK-01 through LOCK-06 all read Complete. DEVTEST-01 stays Pending — its host half is Phase
121, per Plan 119-09's amendment. No other requirement row was touched by this plan.**
