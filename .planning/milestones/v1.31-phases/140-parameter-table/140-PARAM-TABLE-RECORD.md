# 140-PARAM-TABLE-RECORD: Phase 140 Parameter Table — Close Record

**Owner requirements:** TABLE-01, TABLE-02, TABLE-03, TABLE-04, TABLE-05 — all five discharged
**here**, by this plan (140-07), citing the evidence the six prior plans (140-01 through 140-06)
produced. **Status:** the cold measurement this document reconciles was taken strictly after
`140-PREDICTIONS.md` was committed; every reconcilable prediction matched its observation exactly;
both named divergences are recorded below, not smoothed; TABLE-01 through TABLE-05 are marked
complete in `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md` by this same plan's Task 3.

This document follows `138-BASELINE.md`'s house shape (numbered sections, a findings register with
owners, an explicit "what this is and is not" section, a hand-off table), adapted to the eleven
sections this plan's own Task 2 specifies.

---

## 1. What shipped

- **The parameter table type** — `eprom_params_t`, a six-column `struct` (`overprogram_cap_us`,
  `energy_cap_us`, `max_pulses`, `overprogram_factor`, `verify_mode`, `vpp_path`, in that order,
  `static_assert(sizeof == 12)`), plus the `VERIFY_PER_PULSE`/`VERIFY_PER_PULSE_PLUS_FINAL` and
  `VPP_PATH_DROP_RESISTOR`/`VPP_PATH_DIRECT_VPE` enums: `firestarter/include/eprom_params.h`.
- **The table data and accessor** — `EPROM_PARAM_KEYS[]` / `EPROM_PARAMS[]`, two `PROGMEM` arrays
  carrying exactly three rows (`0x07`, `0x08`, `0x0B`), and `eprom_params_for()`, a linear-scan
  accessor with no `switch` and no default row: `firestarter/src/proms/eprom_params.cpp`.
- **The accessor's fail-closed contract (D-05)** — `eprom_params_for()` returns `NULL` for any
  protocol not carried by the table. Proven for both `0x0C` (an adjacent, unrecognized value) and `0`
  by a running test, `test_unknown_protocol_returns_null`, in
  `firestarter/test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp` — never asserted
  from source reading alone.
- **The fifth native env, on the `native_trace_v131` precedent (D-11)** — `[env:native_params_v131]`
  in `firestarter/platformio.ini`, naming only its own suite in `test_filter`, never folded into
  either pinned env, never in `default_envs`; its suite:
  `firestarter/test/native/avr/test_eprom_params_v131/{host_stubs.cpp,test_eprom_params_v131.cpp}`
  (9 cases).
- **Three new committed gates**, each seen RED on a planted violation before its GREEN was believed
  (D-15 — full accounting in §8):
  1. TABLE-05 firmware half (D-13) — `firestarter/tests/golden/protocol_branch_inventory.json` +
     `firestarter/tests/test_protocol_branch_inventory.py` (7 tests).
  2. TABLE-05 database half (D-12) — `firestarter_app/tests/golden/chip_database_field_inventory.json`
     + `firestarter_app/tests/test_chip_database_field_inventory.py` (8 tests).
  3. TABLE-04/TABLE-01/TABLE-02 citation-coverage gate (D-14) —
     `firestarter/tests/golden/eprom_params_citations.json` +
     `firestarter/tests/test_eprom_params_citations.py` (10 tests).
- **Two corrected documents**, reconciled against the shipped citations in plan 140-06 —
  `firestarter/doc/PROTOCOLS.md` §§1.3 (`0x07`), 1.4 (`0x08`), 1.5 (`0x0B`), plus a datasheet-path
  note under §1; and `firestarter/CLAUDE.md`'s Algorithm Handlers rows for the same three protocols,
  plus the D-11 native-env exception appended to "Reuse pattern for future native tests".

`firestarter/src/proms/eprom.cpp` is **byte-unchanged across the whole phase** (D-10) — re-verified in
this plan's own Task 1: `git -C /workspaces/firestarter diff --quiet -- src/proms/eprom.cpp` exits 0,
and `native_trace_v131` (D-10's frozen pre-change fixture) still reports 5/5 PASSED, cold, in this
plan's own measurement (§7). Nothing in `src/` reads the new table yet; Phase 141 wires it in.

## 2. The row values as shipped

| protocol | overprogram_cap_us | energy_cap_us | max_pulses | overprogram_factor | verify_mode | vpp_path |
|---|---|---|---|---|---|---|
| `0x07` | 75000 | 0 | 25 | **0** | `VERIFY_PER_PULSE_PLUS_FINAL` | `VPP_PATH_DROP_RESISTOR` |
| `0x08` | 75000 | 0 | 25 | 0 | `VERIFY_PER_PULSE_PLUS_FINAL` | `VPP_PATH_DROP_RESISTOR` |
| `0x0B` | 75000 | 50000 | 255 | 0 | `VERIFY_PER_PULSE` | `VPP_PATH_DIRECT_VPE` |
| `0x0C` (unrecognized) | — | — | — | — | — | `eprom_params_for(0x0C) == NULL` (D-05) |

Per-cell attribution (vendor, part, document, revision, section, verbatim quote, D-09 scope clause, or
the `"no datasheet basis — reasoned from X"` form) lives in
`firestarter/tests/golden/eprom_params_citations.json` — this record points at that sidecar rather
than restating its 18 cells; the sidecar is the gate-enforced, machine-readable authority, and its
own `test_recorded_values_match_the_live_table` test is what keeps this grid honest against the live
`EPROM_PARAMS[]` initializers.

## 3. Named divergence 1 — `0x07 overprogram_factor = 0`

**Operator decision, 2026-08-09: `0` ships, on three bases**, quoted from the shipped citation
(`eprom_params_citations.json`, cell `(0x07, overprogram_factor)`, `notes`):

1. **Behaviour-preserving** against `firestarter/src/proms/eprom.cpp:161-178` — the firmware's
   existing retry loop is escalation of `pulse_delay`, not an Intel `3×N` margin pulse, on any
   protocol today; shipping `3` on `0x07` would be an unvalidated behaviour change to all 170 chips
   the row carries.
2. **All three `0x07` datasheets read specify no overprogram** — Winbond W27C512 Rev A4 (no
   overprogram step in either algorithm flowchart), ST M27C512 Rev 3 §2.6 (verbatim: *"a sequence of
   100us program pulses are applied to each byte until a correct verify occurs. No overprogram pulses
   are applied since the verify in MARGIN MODE provides the necessary margin"*), Microchip 27C512A
   DS11173G §1.6 (Fig. 1-3 flowchart, no overprogram step) — together covering 113 of the row's 170
   chips.
3. **D-06's precedent** that a primary datasheet beats `PROJECT.md`'s own derived throughput table on
   a tie (§4 below is D-06's own instance, for `0x08`).

**The scoped divergence, stated plainly, not smoothed:** `.planning/PROJECT.md`'s "Expected throughput
(512-byte Uno block)" table gives `0x07` an overpulse of `3 × N × pulse, cap 75 ms` — i.e., it implies
`overprogram_factor = 3`, not the `0` this phase ships. The 22 Intel-family 1 ms parts on this row
(Intel 2764 / 2764A / 27128 / 27128A / 27512, TI TMS2764, NEC UPD2764, ST M2764A, and the rest of the
1000-microsecond sub-population measured in Phase 138's pulse distribution) genuinely want a `3 × N`
margin pulse — that is what "Intel Intelligent Programming" specifies for that silicon generation.
The three `0x07` datasheets actually read for this table's citation do not apply to that sub-population
(they cover the 100 µs-modal 28-pin EEPROM-class parts, 113 of 170 chips); serving the Intel-family
1 ms parts correctly would require **splitting `0x07` into a second row keyed on something other than
`protocol_id`**, which TABLE-05's single-dispatch-key constraint forbids in this milestone.

**Recorded as a Phase 146 follow-up candidate** (evidence: F-140-05), not silently dropped. This is a
genuine, named tension between "ship the value the datasheets actually read for this row support" and
"serve every chip PROJECT.md's throughput table implicitly promised" — this phase chose the former and
says so.

## 4. Named contradiction — `0x08 overprogram_factor = 0`

`.planning/PROJECT.md` contradicts **itself** on this cell, and the contradiction is named here rather
than silently resolved:

- **The prose** (§"Target features"): *"Overprogram pulse — `3 × N × pulse` capped at 75 ms where
  `overprogram_factor > 0`. Correct for older Intel 'Intelligent' 27C parts; **not** for Quick-Pulse /
  Flashrite / PRESTO, so it is gated per row and never applied blanket."* `0x08` is `PROTO_EPROM_32PIN`
  / the Quick-Pulse/Flashrite/PRESTO II family in this firmware — the prose says this row should be
  gated **out** of overprogram.
- **The table** (§"Expected throughput (512-byte Uno block)"): the `0x08` row lists `overpulse:
  3 × N × pulse` — no gating, the same formula as `0x07`. This directly disagrees with the prose two
  paragraphs above it in the same document.

**D-06 resolves this in favour of the prose, on a tie-break: primary datasheets win.** Three
independent vendors researched for this row all specify no overprogram pulse: AMD Am27C020 (FINAL) —
Flashrite description contains no overprogram step; ST M27C1001 §2.6, verbatim: *"...applying a
sequence of 100us program pulses to each byte until a correct verify occurs... No overprogram pulse is
applied since the verify in Margin mode provides necessary margin to each programmed cell"*; Winbond
W27C020 (Preliminary) — SMART PROGRAMMING ALGORITHM flowchart, no overprogram step. `0x08` ships
`overprogram_factor = 0`, agreeing with the prose and contradicting the table. Naming the contradiction
is the requirement TABLE-04 asks for; quietly picking a value and moving on would have been the failure
mode. Phase 146 / CLOSE-04 reconciles `PROJECT.md`'s throughput table text against this finding — this
phase does not edit `PROJECT.md`.

## 5. The `overprogram_cap_us` column is inert on every row

`overprogram_cap_us = 75000` (µs) ships identically on all three rows — `0x07`, `0x08`, and `0x0B` —
and the overpulse clamp `min(3 × N × pulse, cap)` evaluates to `0` on every row today because
`overprogram_factor` resolved to `0` everywhere (§§3-4). TABLE-01 names this column explicitly, so it
ships even though nothing currently reads a nonzero value out of it; every cell is cited as
**reasoned**, not datasheet-derived (the figure itself — `3 × 25 × 1000 µs`, the Intel Intelligent
worst case — is the exact number publicly cited on gh#15's own correction, "the 32-bit-safe helper is
needed for the 75 ms overprogram pulse"), and each cell's citation says explicitly that it is inert
while `overprogram_factor` stays `0`.

Milestone decision D-08 states the cap applies "on both overprogramming rows" — that phrase
**presupposed two such rows would exist in this milestone**. Research found none: `0x07` and `0x08`
both resolved `overprogram_factor` to `0` (§§3-4). The column is not a dead letter — a future Phase 146
family split of `0x07` (§3's follow-up candidate) would immediately need it — but as shipped in Phase
140, it is reasoned, explicitly inert, and honestly labelled that way rather than left to look
load-bearing.

## 6. Prediction versus measurement

`140-PREDICTIONS.md` (P1-P5) was authored and committed by plan 140-01 at commit
`a2705cfb02d848ab1d927da0b784f959300cc4ab` (meta repo, branch
`gsd/v1.31-27c-programming-algorithm-fidelity`), timestamped `2026-08-10T00:13:30Z` — **before** any
cold measurement in that document or this one was taken. This plan's own Task 1 cold capture ran
strictly after that commit, on 2026-08-10, and is the measurement every prediction below is judged
against.

| # | Prediction (quoted) | Measured (this plan, cold) | Match |
|---|---|---|---|
| P1 | "a flash-used delta of approximately 0 bytes against the Phase 138 baseline (`23954`/`24004`/`26016` bytes ... `uno`/`uno328pb`/`leonardo`)" | `uno` 23954, `uno328pb` 24004, `leonardo` 26016 — **delta 0 on all three**, cold, this session | Yes — exact, not merely approximate |
| P2 | "RAM-used stays at `1573`/`1579`/`2014` bytes ... an exact-zero delta, not merely a small one" | `uno` 1573, `uno328pb` 1579, `leonardo` 2014 — **delta 0 on all three** | Yes — exact |
| P3 | "`check_build_warnings.py` against cold logs from both pinned native envs reports `total warnings=1166` for **both**, and exits 0" | `PASS: native: total warnings=1166 (== watermark 1166), native_nodevtools: total warnings=1166 (== watermark 1166)`, exit 0 | Yes — exact |
| P4 | "`native`/`native_nodevtools` both report 141 test cases across 17 suites, all passing. `native_trace_v131` reports 5 test cases across 1 suite, GREEN" | `native` 141/141/17 PASSED; `native_nodevtools` 141/141/17 PASSED; `native_trace_v131` 5/5/1 PASSED | Yes — exact |
| P5 | "passing `native_params_v131` to `check_size_baseline.py` will raise an uncaught `KeyError` (exit 1) ... passing it to `check_build_warnings.py` will exit 2 cleanly" | **Not independently re-triggered this session** — this plan's own critical hazard #2 forbids invoking either script with that env name. Basis unchanged since F-138-05 (Phase 138, static-code-confirmed: `NATIVE_ENVS` hardcoded, `compare_native` bare dict lookup). `native_params_v131`'s own counts (9/9/1, cold, this session) are recorded directly instead, per the `native_trace_v131` precedent | Not re-tested — a deliberate abstention, not a miss |

**No contradiction was found.** Every prediction that this plan's own verification discipline permits
re-testing (P1-P4) matched its cold observation exactly — not merely within a tolerance band. P5's
underlying mechanism (F-138-05) was not re-exercised, by design, because doing so would require calling
one of the two check scripts on an env name both are documented to mishandle, which the plan's critical
hazard #2 forbids; this is recorded as a deliberate non-test, not glossed over as a pass.

**Why the AVR flash delta is exactly 0, mechanically, not by luck:** `configure_eprom` and every other
`src/` call site are untouched this phase (D-10) — nothing in `src/` yet references
`eprom_params_for()`, `EPROM_PARAMS[]`, or `EPROM_PARAM_KEYS[]`. AVR builds pass
`-ffunction-sections`/`-fdata-sections` (compile) and `-Wl,--gc-sections` (link) —
confirmed present in this environment's installed `atmelavr` platform package (F-140-02) — so every
function and every `PROGMEM` array lands in its own linker section, and a section nothing references is
dropped entirely at link time. **The real flash cost of this table — 3 rows × 12 bytes of `PROGMEM`
data, plus the `eprom_params_for()` accessor body — lands in Phase 141's flash delta instead**, funded
by LOOP-02's planned removal of `program_mismatched_bytes()` / `verify_and_update_mask()` /
`NUMBER_OF_RETRIES` / the adaptive growth formula. A ~0 delta here is the **predicted** outcome of a
garbage-collected, not-yet-referenced table — not evidence the table was forgotten (T-140-28's
mitigation). Phase 144 / TEST-08 is where the full-phase (140-143) delta is reconciled against the sum
of every phase's individual prediction, including this one.

## 7. Suite and env counts

| Env / suite | Baseline (Phase 138 / start of 140) | This plan's cold measurement | CI coverage |
|---|---|---|---|
| `native` | 141 cases / 17 suites | **141 / 17**, PASSED | `build.yml` / `beta-build.yml` |
| `native_nodevtools` | 141 cases / 17 suites | **141 / 17**, PASSED | `build.yml` / `beta-build.yml` |
| `native_trace_v131` | 5 cases / 1 suite | **5 / 1**, PASSED | **none** — local run-by-name only |
| `native_params_v131` | (created plan 140-04) | **9 / 1**, PASSED | **none** — local run-by-name only |
| firmware `pytest tests/ -q` | 227 passed | **244 passed** (227 + 7 from 140-02 + 10 from 140-05) | `build.yml` |
| app `pytest tests/ -o addopts="" -q` | 1539 passed | **1547 passed** (1539 + 8 from 140-03) | `ci.yml` |

**`native_params_v131` and `native_trace_v131` run in no CI leg of either repository (F-140-11).**
Neither `firestarter/.github/workflows/build.yml` (lines 142, 155) nor `beta-build.yml` (lines 122,
128) invokes any env beyond `native` and `native_nodevtools`. Their counts above are **local run-by-name
obligations** (D-11) — recorded here as this phase's evidence, never implied to be CI-covered. A future
green CI run for this branch is not, by itself, proof either suite still passes; re-running both by
name, cold, is the only way to know.

## 8. Gate evidence index

Three new gates were authored this phase; **D-15 requires each to be seen RED on a planted violation
before its GREEN is believed.** Total planted RED runs across all three: **3 + 4 + 5 = 12.** No gate's
GREEN was believed before its own RED — verified per-gate below.

| Gate | Path | Tests | Planted RED runs | Verbatim transcripts |
|---|---|---|---|---|
| TABLE-05 firmware half (D-13, protocol-branch inventory) | `firestarter/tests/test_protocol_branch_inventory.py` | 7 | 3 (Run A: new protocol-keyed site; Run B: new non-inventoried handle-field site; Run C: vacuous/empty scan target) | `140-02-SUMMARY.md` §"Planted-Violation Proof (D-15)" |
| TABLE-05 database half (D-12, chip_database.json field inventory) | `firestarter_app/tests/test_chip_database_field_inventory.py` | 8 | 4 (Run A: new field on one chip; Run B: count change, no new name; Run C: vacuous `{}` target; Run D: new key in the generator only) | `140-03-SUMMARY.md` §"Planted Violations (D-15) — Verbatim Transcripts" |
| TABLE-04/01/02 citation-coverage gate (D-14) | `firestarter/tests/test_eprom_params_citations.py` | 10 | 5 (Run A: value with no citation; Run B: citation for a nonexistent value; Run C: D-09 scope blanked on exactly one cell; Run D: drifted value; Run E: pulse-width column injected) | `140-05-SUMMARY.md` §"Planted-Violation Runs (D-15)" |

**3 + 4 + 5 = 12**, matching this phase's own accounting in `.planning/ROADMAP.md`'s Phase 140 detail
section exactly. Each planted run in the cited SUMMARY failed for the reason it was planted to fail —
never a decode/import/path error (D-15 trap 2) — and each gate's own real-tree run (captured
immediately after its planted runs, in the same SUMMARY) was independently confirmed GREEN before this
plan's own Task 1 re-ran the full suites cold (§7) and found all three still passing.

## 9. What is NOT verified by this phase — stated, not implied

- **No bench oracle exists for TABLE-03.** 0 of the 329 shipped 27C chips (`0x07`/`0x08`/`0x0B`
  combined) yields `pulse_delay == 0` (F-140-04) — every real chip in the database supplies a nonzero
  pulse width, so no bench run can ever reach the `pulse_delay == 0` fallback branch this phase's
  native suite exercises. The native suite (`native_params_v131`, cases 1-3 and 4-6) is the **only**
  oracle that can ever prove this behaviour; Phase 145's bench work covers the per-byte loop itself,
  never this particular branch.
- **`0x07`'s `overprogram_factor` value is not validatable by any test in this phase.** The table is
  unreferenced by `src/` (D-10) — there is no running code path this phase can exercise it through.
  It is a data-correctness question settled by attribution (§3) and an explicit operator decision, not
  by an assertion; the gates this phase ships prove the *citation* is present and matches the *shipped
  value*, never that the shipped value is the "right" one for all 170 chips on the row.
- **The ~6.25 V program-VCC and every datasheet's raised-VCC verify pass are unreachable on this
  hardware.** The RURP shield has no VCC-raise path. This is the milestone's evidence ceiling, fixed
  before any code moved, and it is why D-02 forbids a verify-VCC column on this table outright — the
  column would only ever record a value the firmware has no way to act on. `verify_mode` encodes WHEN
  to verify, never at what VCC (recorded in the sidecar's own `meta.evidence_ceiling`, quoted in full
  in `140-05-SUMMARY.md`).
- **`check_size_baseline.py` and `check_build_warnings.py` are structurally blind to
  `native_params_v131`** (F-138-05, inherited from Phase 138 and accepted, not fixed; owner `henols`).
  `check_size_baseline.py` hardcodes `NATIVE_ENVS = ("native", "native_nodevtools")` and
  `compare_native` does a bare dictionary lookup — an unrecognized env name raises an uncaught
  `KeyError` (exit 1, a false regression signal), not the documented exit-2 configuration-error path.
  `check_build_warnings.py` exits 2 cleanly for the same env, for want of a baseline entry. Neither
  script was invoked with `native_params_v131` or `native_trace_v131` anywhere in this phase.

## 10. Findings register

Every finding raised anywhere in Phase 140, with a named owner and a disposition. All are **recorded,
not fixed** (D-07's phase-138 precedent, restated here), except the corrections to prior documents,
which are text corrections landed in-phase (140-06) and named here for completeness.

| ID | Mechanism | Owner | Disposition |
|---|---|---|---|
| F-140-01 | Any TU including both `<Arduino.h>` and the `avr/pgmspace.h` shim emits exactly 14 ArduinoFake macro-redefinition warnings against a native watermark sitting at exactly 1166 (zero headroom) | henols (design constraint of the ArduinoFake shim) | Recorded. Avoided in-phase by following the `src/proms/not_implemented.cpp` shape for `eprom_params.cpp` (no `<Arduino.h>`) — confirmed zero added warnings, cold, both this plan's Task 1 and plan 140-01's own measurement. |
| F-140-02 | The AVR toolchain's `-ffunction-sections`/`-fdata-sections`/`-Wl,--gc-sections` combination drops an unreferenced `PROGMEM` table and its accessor entirely at link time | n/a (toolchain behaviour) | Mechanical basis for §6's ~0 AVR flash delta finding; consumed by Phase 141 / Phase 144-TEST-08's reconciliation. |
| F-140-04 | 0 of 329 shipped `0x07`/`0x08`/`0x0B` chips carry `pulse_delay == 0` in `chip_database.json` — no bench run can ever reach the fallback branch | Phase 145 (bench scope note); TABLE-03 (native-only oracle) | Recorded, not fixed — it is a database-shape fact, not a defect. Named explicitly in §9 so no future reader assumes bench coverage exists for this branch. |
| F-140-05 | `PROJECT.md`'s throughput table implies `overprogram_factor = 3` for `0x07`; the shipped value is `0`; the 22 Intel-family 1 ms parts on this row genuinely want the `3×N` margin pulse the shipped datasheets for this row do not specify | Phase 146 (follow-up candidate: a possible `0x07` family split) | Recorded, not fixed this milestone — splitting `0x07` is a second dispatch key, forbidden by TABLE-05 here. Full statement in §3. |
| F-140-07 | The justification sentence published on gh#15 and carried in `PROJECT.md` for `0x0B`'s `energy_cap_us = 50000` — "`100 × 500 µs` is exactly the classic 2716 *total* programming time" — is factually wrong. The TI TMS 2516 datasheet states its own total programming time for all bits is **100 seconds**, not 50 ms; 50 ms is the *per-location pulse width* (`t_w(PR)` TYP), not a total | Phase 146 / CLOSE-04 (reconciles the posted gh#15 text and `PROJECT.md`'s prose) | Recorded, not applied here. The **value** (50000 µs) is correct and has a genuine primary datasheet basis (`t_w(PR)` = 45/**50**/55 ms); only the published **reason** is wrong. This phase does not edit gh#15's posted comment or `PROJECT.md`'s prose — Phase 146 owns reconciling the published text. |
| F-140-09 | `firestarter/doc/PROTOCOLS.md` §§1.3-1.5 asserted a "JEDEC Intelligent Programming (1 ms pulse × N + 3× overpulse)" / "Same Intelligent Programming algorithm" claim for all three of `0x07`/`0x08`/`0x0B`, citing a nonexistent `W27C512.pdf p.7 §6.2 Programming Algorithm` section — contradicting the datasheets this phase actually read (none of the three rows' representative datasheets specify an overprogram step, and `0x08`/`0x0B` are structurally different algorithm families from `0x07`, not "the same") | henols (documentation accuracy) | **Corrected in plan 140-06** — the false claims and the nonexistent citation were removed from `doc/PROTOCOLS.md` §§1.3-1.5 and replaced with the datasheet-grounded facts this phase's citation sidecar ships, each pointing at `tests/golden/eprom_params_citations.json`. Verbatim removal proof: `140-06-SUMMARY.md` §"Removal Proof". |
| F-140-10 | `140-RESEARCH.md`'s Pitfall 5 named a three-site "other" branch-predicate inventory for `src/proms/eprom.cpp` (`:145`, `:218`, `:320`) beyond the one algorithm-selector switch (`:71`); the D-13 gate's actual, complete, independently re-derived scan of the same file found **21** tier-2 (non-protocol-keyed) sites, not 3 — roughly twenty pre-existing handle-field predicates the research pass's narrower table never enumerated | henols (research scope, not a defect — `140-RESEARCH.md` is left unedited per this project's standing convention) | Recorded here as the corrected, complete count. This is exactly why D-13's gate pins a full two-tier inventory (3 tier-1 protocol-keyed + 21 tier-2, classified and reasoned) rather than attempting to forbid a generic "class" of branch — a rule written against Pitfall 5's 3-site preview would have been silently incomplete against the real 24-site population. See `140-02-SUMMARY.md` for the full derivation. |
| F-138-05 (inherited) | `check_size_baseline.py`'s `compare_native` raises an uncaught `KeyError` (exit 1) rather than exit 2 for an env absent from the baseline; `check_build_warnings.py` exits 2 cleanly for the same condition | henols | Recorded, not fixed (D-07 precedent). Both gates remain structurally blind to `native_params_v131` and `native_trace_v131` — neither was invoked with either name anywhere in Phase 140 (§9). |

## 11. Hand-offs

| Downstream | Consumes |
|---|---|
| **Phase 141 (Per-Byte Program Loop)** | The table itself (`eprom_params_t`, `eprom_params_for()`, all six columns) — Phase 141's loop is the first `src/` code to call `eprom_params_for()`. The real AVR flash cost this phase's ~0 delta deferred (§6) lands in Phase 141's own measurement, funded by LOOP-02's removals. |
| **Phase 142 (High-Voltage Routing)** | `vpp_path`'s two values and their consumers; the duplicated `0x0B \|\| FLAG_VPE_AS_VPP` VPP branch at `eprom.cpp:145` and `:218`, inventoried (not touched) by this phase's D-13 gate — Phase 142 will legitimately turn that gate RED when it rewires the branch, and must re-derive the inventory (never hand-edit it) when it does. |
| **Phase 144 / TEST-08** | §6's prediction-versus-measurement table and its mechanical `--gc-sections` explanation — TEST-08 reconciles the full-phase (140-143) flash/RAM/warning/suite-count delta against the sum of every phase's individual prediction, including this one. |
| **Phase 144 / TEST-06** | The still-GREEN `native_trace_v131` frozen fixture (§1, §7) — TEST-06 diffs the *new* (post-loop-rewrite) trace against this same frozen baseline; a divergence there is expected work under v1.31, not a regression. |
| **Phase 146 / CLOSE-04** | F-140-05 (§3, the `0x07` Intel-family split candidate), the `0x08` contradiction (§4, D-06), and F-140-07 (§10, the wrong "100 × 500 µs" gh#15 justification) — CLOSE-04 reconciles `PROJECT.md`'s throughput table text and the posted gh#15 comment against these findings. This phase named all three; it edited none of the published text. |

---

*Phase: 140-parameter-table — Plan 07*
*Recorded: 2026-08-10, from this plan's own cold Task 1 measurement and the six prior plans'
committed SUMMARY.md artifacts (`140-01-SUMMARY.md` through `140-06-SUMMARY.md`), the shipped
`tests/golden/eprom_params_citations.json` sidecar, `.planning/PROJECT.md`, and
`.planning/phases/140-parameter-table/140-RESEARCH.md`.*
