---
phase: 153-write-path-erase-policy
plan: 16
status: complete
created: 2026-08-21
---

# Phase 153: Write-Path Erase Policy — Outcome Record

This is the phase's own record of what it shipped, what was proven and how, and — with equal
weight — what was **not** proven. It summarises rather than restates `153-DECISIONS.md`
(`D-153-01`…`D-153-05`) and the fifteen prior plan SUMMARYs; those documents carry the full
evidence trail. Phase 152 drafts outward-facing text from this file and runs immediately after
this phase closes, so a claim that is not true here becomes a public overclaim there.

## What shipped

**ERASE-01.** `write` performs no blank check on protocol `0x0D` (28C family), with or without
`FLAG_SKIP_BLANK_CHECK`. The three-line conditional at `eeprom_28c.cpp:517-519` was deleted
outright, not re-gated, and `mem_util_blank_check` now appears exactly once in the file — the
`CMD_BLANK_CHECK` dispatch arm. Delivered in `153-02` (code, proven by an observed-RED-then-GREEN
native case) and `153-13` (the last false prose claim, `doc/PROTOCOLS.md` §1.6's "`-b` is
required" recommendation, removed).

**ERASE-02.** The same policy holds for protocol `0x05` (flash4). Its sibling conditional was
**located in code before being touched**, not assumed by symmetry: `flash_5v_page.cpp:88-90`
(`153-06` confirmed this is `153-RESEARCH.md`'s original figure — see Mechanism Corrections
below for the drifted "87-89" claim this disproved). Deleted the same way, proven the same way.
Delivered in `153-06` (code) and `153-13` (doc, `PROTOCOLS.md` §1.1 gained one sentence stating
the write path performs no blank check on `0x05` either, for the same per-page auto-erase reason,
while keeping algorithm 5's distinct hardware-hazard exclusion unconflated with algorithm 13's
retired one).

**ERASE-03.** `erase` is available as a standalone step on `0x0D`. A `case CMD_ERASE:` arm in
`configure_eeprom28c` dispatches to a real operation (`153-03`), proven to actually emit the
AN-0544B stream rather than merely resolve a non-NULL pointer (`153-04`). `FLAG_CAN_ERASE` is
restored on the wire for all 84 algorithm-13 rows at `database.py:617` (not `:621` — see Mechanism
Corrections), with algorithm 5 staying excluded for its own, unrelated hardware-hazard reason
(`153-07`). The wire-level and host-level ripple this restoration causes was proven exhaustively:
an 84-entry, field-disjoint delta layer over the Phase 149 golden (`153-08`); inverted
conversion/wire-shape assertions with both negative controls (UV-EPROM, algorithm 5) left
byte-unchanged (`153-09`); the `dev test` plan-shape ripple, including the AT28C256 blank-check
placement's exact measured index (`153-10`); the corrected `write --skip-erase` warning
(`153-11`); an exhaustive whole-database proof that exactly 84 of 746 rows changed and 0
non-algorithm-13 rows moved (`153-12`); and the two remaining false prose sites (`153-13`).

**ERASE-04.** The erase implements the **software 6-byte** AN 0544B sequence, never the
datasheet's 12 V-on-OE hardware path. `eeprom28c_erase_execute` emits the SDP-disable prefix
(`D-153-02`) then the six inline `firestarter_set_data` writes, 0 B RAM by construction (`153-03`).
Its emitted stream is pinned against the tree at head, tail and divergence index — never a
retyped literal, never a bare `!= -1` (`153-04`). `tools/check_dispatch.py` (GATE-03) is
unweakened, unexempted and un-re-baselined — `git diff --quiet` holds and its invariant suite is
green — and the phase built the control that actually guards this hazard,
`scripts/check_erase_no_vpp.py`, proven both reachable (fails on a committed planted violation)
and discriminating (fails on `eeprom28c_check_chip_id`'s legitimate A9-12V writes) (`153-05`, the
plan that owns this requirement's flip).

**ERASE-05.** `blank` remains available as its own step. This was a non-regression assertion, not
new work: `cli_handlers.py:854` → `CMD_BLANK_CHECK` → `mem_util_blank_check` already worked before
this phase and is proven still to work across the CLI, host-call and firmware-dispatch layers
(`153-12`).

**ERASE-06.** `info`'s "can be erased" row agrees with the wire flag instead of contradicting it.
No `ic_layout.py` edit was needed: that file's `can_erase_str` derivation keys on
`electrical.type` alone and already said "yes" for algorithm-13 chips before this phase; ERASE-03
restoring the wire flag makes the two axes agree as a by-product. Proven both-directions, for an
affirmative case (AT28C256) and a negative control (AM27512, UV-EPROM) (`153-12`).

**ERASE-07.** The stale Phase 121 D-12 code comment at `database.py:585-616` (the false sentence
at `:589-592`) is corrected in place, in the project's established reversal-record voice —
mechanism-corrected and intent-satisfied, never framed as a prior failure. This is the **fourth**
recorded reversal in this comment's chain (Phases 119 → 120 → 121 → 153; see Mechanism
Corrections). Delivered in `153-07`, which also performed the ERASE-03 host-side edit this
requirement's comment describes.

**ERASE-08.** Constants stay in lockstep across `firestarter/include/firestarter.h` and
`firestarter_app/firestarter/constants.py` (`CMD_ERASE`, `CMD_BLANK_CHECK`, `FLAG_CAN_ERASE`,
`FLAG_SKIP_ERASE`, `FLAG_SKIP_BLANK_CHECK` — every value identical, confirmed by
`test_revision_constants_parity.py`). The flash/RAM delta was measured cold on all three AVR
targets against the pre-change baseline: **+130 B flash, +0 B RAM** on `uno`, `uno328pb` and
`leonardo` alike, verifying `D-153-01`'s RAM-neutral prediction rather than merely asserting it.
`leonardo` was funded with a fourth named, SHA-attributed MERGE-05 exemption,
`MERGE05_ERASE_STANDALONE_EXEMPTION_BYTES = 130`, sized exactly from the measured delta and never
rounded (`153-14`). The size tripwire was then re-planted on a new, thirteen-file `*_v153*`
fixture family — never repointing or re-anchoring the retired `*_v151*` family — with every plant
observed flipping the checker to failure before any leg trusted it (`153-15`, which owns this
requirement's flip).

**ERASE-09.** The change is stated, in this record and in every phase artifact that touches it,
**software-proven and unvalidated on silicon**. `153-01` first put the phrase on the record
before any code was written; this plan (`153-16`) is the phase's closing statement of it and the
one that flips the requirement (see "What was NOT proven" below and the Requirement Flip section).

## What was proven, and how

- **The write-path removal (ERASE-01/02)** is proven by native cases asserting single-shot INIT —
  `is_operation_in_progress` FALSE after exactly one `write_init` call with the skip flag clear —
  observed FAILING before the deletion and PASSING after, on both `0x0D` (`153-02`) and `0x05`
  (`153-06`).
- **The erase stream (ERASE-04)** is proven by three native cases pinning
  `eeprom28c_erase_execute`'s emitted stream against the tree, never against retyped prose: head
  equality with `SDP_FIXED_DIP28_28C256` (Case 31), the terminal payload equal to `FLASH_ERASE`'s
  own last byte rather than `EEPROM_SDP_DISABLE`'s (Case 32, the one-nibble hazard class Case 19
  already exists for), and an **exact** divergence index against a bare chip-erase-only reference
  — `SDP_FIXED_DIP28_28C256_LEN - 3`, measured at 51, never `!= -1` (Case 33) (`153-04`).
- **The absence of any programming-rail write (ERASE-04's GATE-03 half)** is proven by
  `scripts/check_erase_no_vpp.py`, a brace-matched negative source scan of
  `eeprom28c_erase_execute`'s body, observed FAILING against a committed planted control-register
  write and against a real adjacent function (`eeprom28c_check_chip_id`) that legitimately uses
  those tokens — proving the checker discriminates rather than merely passing (`153-05`).
- **The 84-row scope (ERASE-03)** is proven exhaustively over all 746 database rows, twice: once
  as a wire-value delta layer generated programmatically against a live capture (`153-08`), and
  once as a whole-database invariant asserting exactly 84 rows changed and 0 non-algorithm-13 rows
  moved (`153-12`).
- **The size cost (ERASE-08)** is proven by three cold (`rm -rf .pio/build/<env>` then one
  `pio run`) builds on all three AVR targets, transcribed in `153-DECISIONS.md`, and by both
  `check_size_baseline.py` gate modes exiting 0 against the revised baseline and against
  `size_baseline_base01.json` with BASE-01 named explicitly.

## What was NOT proven

This change ships **software-proven and unvalidated on silicon.** No AT28C part was involved at
any point in this phase — not in writing the erase sequence, not in choosing the SDP-disable
prefix, not in any test. Removing a blank check, restoring a capability flag, and pinning a byte
stream against in-tree tables are all software facts; none of them is evidence that a physical
AT28C part actually erases when this code runs.

Stated as plainly as the outcomes above:

- **`0x0D` stays `UNVERIFIED`** in `PROTOCOL-LEDGER`. Nothing in this phase graduates it.
- **No `support_status` field moved.** `tools/check_no_community_support_status_write.py` and
  `tools/check_diagnostic_report_claims.py` both exist to machine-check this and both exit 0
  against the tree this phase leaves behind; `chip_database.json` is byte-unchanged
  (`git diff --stat` empty).
- **gh#21, gh#11 and gh#12 stay OPEN.** A code fix is not a validation. *(Record correction 2026-08-21, found by the phase-153 verifier: **gh#32 was already CLOSED on 2026-08-08**, two weeks before this phase, as an unrelated duplicate-fold into gh#21. The no-graduation rule is unchanged and still binds gh#21, gh#11 and gh#12; gh#32 simply is not an open issue to hold. Phase 152 must not "reply" to a closed issue on the strength of this line.)* Only a fresh
  passing `dev test` report from real silicon closes a `dev test` issue, and only
  `devtest-triage` closes it.
- **No AT28C part was required or permitted as a validation dependency at any point** — every
  requirement in this phase's `153-VALIDATION.md` is provable in software, and the ones that are
  *only* provable in software are marked so there.

Two further honest limitations, carried forward from `153-RESEARCH.md` and not resolved by
anything this phase built:

- **The 20 ms `t_EC` cycle-time figure is an Atmel-family maximum**, drawn from AN 0544B, Rev.
  0544B-10/98. The 84-row algorithm-13 bucket spans several other vendors. A part with a longer
  actual cycle time than the Atmel figure would read non-blank after a successful-looking erase —
  nothing in this phase's test suite could catch that, because no such part was tested.
- **No native test can prove the wall-clock wait is honoured.** The native trace stubs do not
  stub `delay()` and record no time, so the assertion that `eeprom28c_erase_execute` actually
  waits `AT28C_TEC_MAX_MS` before returning is structural (the call is present in the source) and
  not temporal (no test measures elapsed time).

## Decisions

| ID | One line |
|----|----------|
| `D-153-01` | Erase supply form: six inline `firestarter_set_data` calls, 0 B RAM — not a new `.data` table. Fourth named MERGE-05 exemption reserved, sized in plan 14 at 130 B. |
| `D-153-02` | The `0x0D` chip erase emits an SDP-disable prefix first, on an asymmetry argument (an undetectable phantom erase is worse than six harmless extra bus writes on an already-unprotected part) — not on the application note's silence. |
| `D-153-03` | `check_dispatch.py`'s GATE-03 guard is DB-and-dispatch-table scoped and cannot see a handler-body control-register write. The real primary control is a brace-matched negative source scan (plan 05); `check_dispatch.py` itself stays byte-unchanged and independently verified. |
| `D-153-04` | No post-erase blank check is wired on `0x0D` (`erase -b` is a documented no-op); `erase --sector-address` is ignored (the AN 0544B sequence is a device-global chip erase by construction). |
| `D-153-05` | `erase` stays standalone: no `FLAG_CAN_ERASE`-gated erase-on-write block added to `eeprom28c_write_init`, and no `--skip-sdp-unlock` option added to `erase`. |

See `153-DECISIONS.md` for the full reasoning, measured figures, and named rejected alternatives
behind each of these.

## Two size figures, separately

- **MERGE-05 `leonardo` flash headroom is 0 B.** Measured delta against `size_baseline_base01.json`
  is `+724 B`, exactly equal to the four-term allowance
  (`band 0 + defect-fix 96 + page-size-seam 210 + lock-status-read 288 + erase-standalone 130 =
  724`). RAM delta against the immediately-prior pre-phase position is `+0 B` on all three
  targets, verifying `D-153-01`'s RAM-neutral form.
- **The Caterina cliff headroom is a separate, UNGUARDED figure: `28672 - 27630 = 1042 B`.** This
  is not a MERGE-05 quantity and is not computed from it. `board_upload.maximum_size` was raised
  to the real 32768 B on all three AVR environments by a prior quick task, so the linker no longer
  protects the USB bootloader boundary — nothing but this recorded number stands between a future
  phase's growth and a bricked `leonardo`.

**These two numbers are never the same number and must never be conflated in any later plan or
outward-facing text.**

## Mechanism corrections made in this phase

- **The GATE-03 criterion's stated mechanism did not hold.** ROADMAP criterion 3 implies
  `tools/check_dispatch.py` is what prevents the hardware 12 V-on-OE erase path from reaching
  `0x0D`. It structurally cannot — that checker is database-and-dispatch-table scoped and never
  looks inside a C++ handler body. The real control this phase built is
  `scripts/check_erase_no_vpp.py` (`153-05`), a brace-matched negative source scan, proven
  reachable and discriminating. `check_dispatch.py` itself was not weakened, exempted, or
  re-baselined — `git diff --quiet -- tools/check_dispatch.py` holds — and is recorded as an
  independently required invariant, never as the hazard-preventing control it cannot structurally
  be (`D-153-03`).
- **The sibling `0x05` conditional was located, not assumed.** `153-RESEARCH.md` originally
  recorded it at `flash_5v_page.cpp:88-90`. `153-PATTERNS.md` later "corrected" that to `87-89`.
  Plan 06 read the file directly before touching it and confirmed the real position is `88-90` —
  line 87 is the closing brace of the unrelated `FLAG_CAN_ERASE` block above it. RESEARCH was
  right; PATTERNS' correction was itself wrong.
- **ERASE-06 needed no source edit, and the adopted reading is recorded.** ERASE-06 was read as
  "the two axes (`info`'s row and the wire flag) must not contradict", not "`info` must derive
  from the wire bit". Under that reading, `ic_layout.py`'s `can_erase_str` block — confirmed at
  `:578-586`, PATTERNS' corrected figure over RESEARCH's original `:581-585`, and this one held —
  needed zero edits: it already keyed on `electrical.type` alone and already agreed once
  ERASE-03 restored the wire flag (`153-12`).
- **ERASE-07's comment is the fourth recorded reversal in its chain.** The Phase 121 D-12 comment
  at `database.py:585-616` has now been corrected, restated, and re-corrected across Phases 119 →
  120 → 121 → 153, each time in the project's established mechanism-corrected /
  intent-satisfied voice, never framed as a failure (`153-07`).
- **A fourth corrected line number, found independently of the above three:** the host edit site
  for ERASE-03 is `database.py:617` (the `algo not in (5, 13)` exclusion tuple itself), not `:621`
  as both `ROADMAP.md` and `REQUIREMENTS.md` state — line 621 is the `simple_flags |=` body that
  reads the tuple's result, not the edit site. `153-RESEARCH.md` caught this before any code was
  written; `153-07` confirmed it by making exactly that one-character edit at the correct line.

## What Phase 152 must not repeat

These claims are now false, and Phase 152's outward-facing text must not state any of them:

- That the `0x0D` / AT28C family has no erase operation at all.
- That the blank-check-skip flag (`-b` / `--no-blank-check`) is required to write a non-blank
  AT28C part.
- That v1.32 has fewer than three firmware-touching workstreams (it has three: Phase 149, Phase
  151, and Phase 153 — corrected in `PROJECT.md` and `ROADMAP.md` by this plan).

And, restated from "What was NOT proven" above because Phase 152 is the phase most likely to
reach for it under public pressure to answer gh#21 optimistically: nothing in this phase is
evidence that the `0x0D` write path works on real silicon, `0x0D` stays `UNVERIFIED`, no
`support_status` changed, and gh#21/#11/#12 all stay OPEN (gh#32 was already closed 2026-08-08).

---

## Full Phase Gate — transcribed from a committed tree

Run 2026-08-21, after committing this plan's Task 1 (`893c3e65`) and Task 2 (`69210c81`) meta
commits. Both sub-repositories confirmed clean of tracked modifications before the run (verified
again after — see "End-of-gate repository state" below).

### ERASE-09's own machine gates

```
$ cd firestarter_app && python3 tools/check_no_community_support_status_write.py; echo exit=$?
PASS: scanned ../firestarter/diagnostic_report.py, parse_devtest_issue.py; 0 support_status writes (sole write locus stays tools/build_db.py)
exit=0

$ python3 tools/check_diagnostic_report_claims.py; echo exit=$?
PASS: scanned /workspaces/firestarter_app/tools/../firestarter/diagnostic_report.py, 167 string literals checked, zero forbidden matches
exit=0

$ git diff --stat -- firestarter/data/chip_database.json
(empty)
```

### Host suite, lint, types (`firestarter_app/`)

```
$ python3 -m pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70 -o addopts="" -q
...
TOTAL                                    5228    857    84%
Required test coverage of 70% reached. Total coverage: 83.61%
32 snapshots passed.
1825 passed, 1 warning in 219.10s (0:03:39)

$ ruff check firestarter/ tests/
All checks passed!

$ ruff format --check firestarter/ tests/
156 files already formatted

$ <python 3.11 venv>/bin/python3 tools/check_mypy_watermark.py
checked 158 source files
mypy errors: 35 (watermark: 35)
OK: error count at watermark.
```

*(The devcontainer's default Python is 3.12; `check_mypy_watermark.py` fails open on it against an
unrelated numpy-stub syntax error. Ran through a throwaway `uv venv --python 3.11` in the session
scratchpad instead — no repository file changed to work around this, matching the environment gap
already on record from plan 15.)*

### Dispatch (GATE-03), SDP-window, cross-repo parity (`firestarter_app/`)

```
$ python3 tools/check_dispatch.py; echo exit=$?
PASS: all 746 chips scanned; 736 supported; 10 chips confirmed non-dispatchable ...; 0 dispatch regressions; 0 consistency violations
exit=0

$ git diff --quiet -- tools/check_dispatch.py; echo undiffed=$?
undiffed=0

$ python3 tools/check_no_log_in_sdp_window.py; echo exit=$?
PASS: no logging call in SDP timing window (.../eeprom_28c.cpp, emitter lines 349-365, completion-poll lines 399-412)
exit=0

$ python3 -m pytest tests/test_sdp_table_parity.py tests/test_dispatch_mirror.py tests/test_check_dispatch_invariants.py -o addopts="" -q
19 passed in 0.38s
```

### Cross-repo gates with the firmware root pointed at a nonexistent path (sibling-absent skip check)

```
$ FIRESTARTER_FW_ROOT=/nonexistent-path-for-skip-check python3 -m pytest tests/test_sdp_table_parity.py tests/test_dispatch_mirror.py -o addopts="" -q -rs
SKIPPED [1] tests/test_sdp_table_parity.py:176: firestarter firmware checkout absent (no /nonexistent-path-for-skip-check/.git marker)
SKIPPED [1] tests/test_sdp_table_parity.py:200: firestarter firmware checkout absent (no /nonexistent-path-for-skip-check/.git marker)
SKIPPED [1] tests/test_sdp_table_parity.py:242: firestarter firmware checkout absent (no /nonexistent-path-for-skip-check/.git marker)
SKIPPED [1] tests/test_sdp_table_parity.py:300: firestarter firmware checkout absent (no /nonexistent-path-for-skip-check/.git marker)
SKIPPED [1] tests/test_dispatch_mirror.py:151: firestarter firmware checkout absent (no /nonexistent-path-for-skip-check/.git marker)
SKIPPED [1] tests/test_dispatch_mirror.py:183: firestarter firmware checkout absent (no /nonexistent-path-for-skip-check/.git marker)
1 passed, 6 skipped in 0.04s
```

Every skip carries a named reason (`firestarter firmware checkout absent — no <path>/.git
marker`), distinguishing a clean skip from an error, per the plan's own requirement.

### Firmware: both native environments (`firestarter/`)

```
$ pio test -e native
================ 170 test cases: 170 succeeded in 00:00:28.379 ================

$ pio test -e native_nodevtools
================ 170 test cases: 170 succeeded in 00:00:32.109 ================
```

Both environments agree at 170 cases / 17 suites, matching `size_baseline.json`'s `native_envs`
block as revised by plan 15.

### Firmware: three cold AVR builds

```
$ rm -rf .pio/build/uno       && pio run -e uno
RAM:   used 1575 bytes from 2048 bytes
Flash: used 25548 bytes from 32768 bytes

$ rm -rf .pio/build/uno328pb  && pio run -e uno328pb
RAM:   used 1581 bytes from 2048 bytes
Flash: used 25598 bytes from 32768 bytes

$ rm -rf .pio/build/leonardo  && pio run -e leonardo
RAM:   used 2016 bytes from 2560 bytes
Flash: used 27630 bytes from 32768 bytes
```

All three byte-identical to `size_baseline.json`'s committed `avr_targets` block and to plan 15's
recorded post-severance position.

### Firmware: both `check_size_baseline.py` gate modes

```
$ python3 scripts/check_size_baseline.py --avr-log uno=... --avr-log uno328pb=... --avr-log leonardo=... --native-log native=... --native-log native_nodevtools=...
PASS: uno(flash=25548/32768,ram=1575/2048), uno328pb(flash=25598/32768,ram=1581/2048), leonardo(flash=27630/32768,ram=2016/2560), native(cases=170,suites=17), native_nodevtools(cases=170,suites=17)

$ python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log uno=...
PASS: uno(flash=25548/32768[+724<=788=band64+exempt96+seam210+lock288+erase130],ram=1575/2048[+2<=2=seam2])

$ python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log uno328pb=...
PASS: uno328pb(flash=25598/32768[+724<=788=band64+exempt96+seam210+lock288+erase130],ram=1581/2048[+2<=2=seam2])

$ python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log leonardo=...
PASS: leonardo(flash=27630/32768[+724<=724=band0+exempt96+seam210+lock288+erase130],ram=2016/2560[+2<=2=seam2])
```

Both modes exit 0 on all three targets. BASE-01 named explicitly in the second command, per the
plan's own requirement.

### Firmware: build-warnings, erase-body, checker-convention, own python suite

```
$ python3 scripts/check_build_warnings.py --log uno=... --log uno328pb=... --log leonardo=... --log native=... --log native_nodevtools=...
PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0), leonardo: macro_redefinition=0 (== 0), native: 998 (168 below 1166 watermark), native_nodevtools: 998 (168 below 1166 watermark)
exit=0

$ python3 scripts/check_erase_no_vpp.py; echo exit=$?
PASS: eeprom28c_erase_execute() in .../eeprom_28c.cpp (lines 545-560, 16 lines scanned) contains no VPP/VPE control-register, chip-enable/disable, or bus-config-bypassing hazard token
exit=0

$ python3 -m pytest tests/ -o addopts="" -q
322 passed in 11.15s
```

The 322-test run includes `test_check_erase_no_vpp.py` (7), `test_checker_convention.py` (7),
`test_check_size_baseline.py` (14), and `test_flash_path_record_sync.py` — all passing, which is
also the whole-repo porcelain assertion those tests carry passing against a committed tree.

### End-of-gate repository state

```
$ git -C firestarter status --short
(empty)

$ git -C firestarter_app status --short
?? .planning/config.json
?? SECURITY.md
?? datasheets/M27C1001.pdf
?? datasheets/M27C512.pdf
?? datasheets/W27C512.pdf
?? datasheets/W27E257.pdf
?? write_test_port.sh
```

`firestarter` carries zero tracked or untracked changes from this plan's gate run. `firestarter_app`
carries zero **tracked** modifications; its six untracked files predate this plan (confirmed
unrelated to Phase 153 in `153-14-SUMMARY.md` and `153-15-SUMMARY.md`) and are not touched by
running the gate. Both sub-repos are left clean of tracked modifications, satisfying this plan's
own success criterion.

## Requirement Flip: ERASE-09

**ERASE-09 is claimed in frontmatter by exactly two plans in this phase: `153-01` and `153-16`.**
This plan is the last of the two and its own frontmatter designates it as the flip's owner
("Requirement flips owned by this plan: ERASE-09").

ERASE-09's full text (`.planning/REQUIREMENTS.md`): *"The change is stated **software-proven and
unvalidated on silicon**, in those terms. Removing a blank check is not evidence the `0x0D` write
path works; no ERASE requirement asserts it does, graduates `0x0D` out of `UNVERIFIED`, changes
any `support_status`, or requires an AT28C part."*

Evidence against each clause:

- **"stated software-proven and unvalidated on silicon, in those terms"** — the verbatim phrase
  appears in `153-DECISIONS.md` (D-153-01(f)), `firestarter/CLAUDE.md`, `firestarter/doc/
  PROTOCOLS.md` §1.6, `firestarter_app/doc/protocol-id.md`'s `0x0D` row,
  `firestarter/tests/test_check_size_baseline.py`'s severance-record docstring, and this record
  (grep count over `.planning/phases/153-write-path-erase-policy/153-RECORD.md` ≥ 1, checked
  above).
- **"no ERASE requirement asserts it does [work], graduates `0x0D` out of `UNVERIFIED`"** — stated
  explicitly in "What was NOT proven" above and cross-checked against every one of ERASE-01…08's
  "What shipped" paragraphs: none claims silicon validation.
- **"changes any `support_status`"** — `tools/check_no_community_support_status_write.py` exits 0
  and `chip_database.json` is byte-unchanged (`git diff --stat` empty), independently verified in
  this plan's own gate run above.
- **"requires an AT28C part"** — no task in any of this phase's sixteen plans names an AT28C part
  as a dependency; `153-VALIDATION.md`'s own "Manual-Only Verifications" table names exactly one
  manual verification (a physical AT28C part actually erasing) and marks it "**Deliberately out
  of scope**".

All four clauses are satisfied with evidence now on record across this plan and `153-01`.
**ERASE-09 is flipped to Complete.** With this flip, **all nine ERASE requirements
(ERASE-01…ERASE-09) read Complete** in `.planning/REQUIREMENTS.md`.
