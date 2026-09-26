# 144-TEST-RECORD: Phase 144 Tests & Build Verification — Test Record

**Owner requirements:** TEST-01, TEST-02, TEST-03, TEST-04, TEST-05, TEST-06, TEST-07, TEST-08 — all eight
discharged **here**, by this plan (144-07), citing the evidence the six prior plans (144-01 through 144-06)
produced. This document follows `143-HOST-RECORD.md`'s house shape (numbered sections, a findings register,
an explicit non-claims section, a hand-off table) — itself following `142-VPP-RECORD.md`'s precedent.

**Scope boundary, stated once and binding for the whole record:** this phase proves what Phases 140–143
built. It adds no algorithm behavior, changes no programming path, and edits **no file under
`firestarter/src/`** (D-04). Every verdict, figure, and non-claim below traces to one of the six committed
plan SUMMARYs (`144-01-SUMMARY.md` through `144-06-SUMMARY.md`), to `144-CONTEXT.md`'s decisions, to
`144-RESEARCH.md`'s verified corrections, or to the gate source files those plans authored — nothing here is
re-measured or recalled from memory. No bench run happened in this phase; no claim about real silicon
appears anywhere below (Phase 145 owns that); no chip's `support_status` changed.

---

## 1. Requirement-to-Evidence Map

### TEST-01 … TEST-05: the native mapping gate

**`firestarter/tests/test_requirement_case_mapping_v131.py`** (144-01, commits `16e5bdc`/`7b2ba16`, 805
lines, 9 tests, all passing) is the machine-checked map. Its own docstring states plainly: *"This module
maps requirements onto pre-existing coverage; it authors no new native `RUN_TEST` case and edits no file
under `src/` (D-04)."* Across all five requirements below, the honest finding is that no new native case was
required — every one was already proven by Phases 140/141/142's own suites, and this gate's job is to prove
the mapping is real (source-parsed, not prose) rather than to add behavior.

The frozen `_REQUIREMENT_CASES` map (`test_requirement_case_mapping_v131.py:298-354`), read directly from
the committed gate source as the single authoritative statement:

| Requirement | Requirement text (REQUIREMENTS.md) | Mapped cases |
|---|---|---|
| **TEST-01** | "Native tests prove `0x07`, `0x08` and `0x0B` each resolve to their own table row." | `test_each_protocol_resolves_to_its_own_distinct_row`, `test_unknown_protocol_returns_null`, `test_row_values_match_the_frozen_table` (3, `test_eprom_params_v131`) |
| **TEST-02** | "Native tests prove fixed-width pulse/verify per byte and that the width does not escalate between attempts." | `test_loop01_pulse_width_never_grows_between_attempts`, `test_loop01_each_byte_gets_exactly_the_seeded_number_of_fixed_width_pulses`, `test_loop01_verify_read_follows_every_pulse`, `test_loop01_a_byte_that_converges_on_its_last_permitted_pulse_succeeds` (4, `test_loop_eprom_v131`) |
| **TEST-03** | "Native tests prove the overprogram duration derives from the successful byte's pulse count and honours `overprogram_cap_us`." | `test_loop03_overprogram_duration_is_three_times_the_pulse_count_times_the_width`, `test_loop03_overprogram_is_zero_when_the_factor_is_zero`, `test_loop03_overprogram_clamps_at_the_cap_rather_than_refusing`, `test_loop03_overprogram_is_32_bit_safe_at_the_uint16_ceiling`, `test_loop03_a_zero_cap_yields_no_overprogram_pulse` (5, `test_loop_eprom_v131`) **plus** `test_loop04_no_live_row_emits_an_overprogram_pulse` as the structural-unreachability witness — see Section 6, item 1 for the bounded non-claim this last case exists to state |
| **TEST-04** | "Native tests prove max-pulse failure aborts the block, reports the address, and disables every high-voltage route." | `test_loop05_a_byte_that_misses_within_max_pulses_aborts_the_block` (the "reports the address" clause is satisfied by the asserted `u24` address + `u8` pulse-count payload **inside** this case, not a separate one), `test_loop05_the_loops_own_strobes_disable_the_high_voltage_route`, `test_loop05_a_successful_block_does_not_disable_the_route` (non-vacuity control), `test_vpp02_x3_the_energy_cap_exit_disables_the_route`, `test_vpp02_x4_the_final_pass_verify_failure_disables_the_route`, `test_vpp02_e1_write_init_error_exit_leaves_no_route_asserted` (6, `test_loop_eprom_v131` + `test_vpp_eprom_v131`) — see Section 6, item 4 for the register-stream-only boundary this requirement's text is **not** narrowed by |
| **TEST-05** | "Native tests prove the `0xFF`/already-matching skips and the `pulse_delay == 0` fallback." | `test_loop06_an_ff_target_byte_is_never_read_and_never_pulsed`, `test_loop06_an_already_matching_byte_is_read_once_and_never_pulsed`, `test_loop06_a_block_of_only_skipped_bytes_emits_no_pulse_at_all`, `test_loop06_the_ff_rule_does_not_suppress_the_final_verify_pass` (4, `test_loop_eprom_v131`) **plus six params cases in two families of three** — see Section 7 (C-04) for why it is six, not the "two fallback cases" `144-CONTEXT.md`'s own prose named: `test_0x07_zero_pulse_delay_takes_the_1000us_fallback`, `test_0x08_zero_pulse_delay_takes_the_100us_fallback`, `test_0x0B_zero_pulse_delay_takes_the_500us_fallback`, `test_0x07_nonzero_pulse_delay_is_left_alone`, `test_0x08_nonzero_pulse_delay_is_left_alone`, `test_0x0B_nonzero_pulse_delay_is_left_alone` (6, `test_eprom_params_v131`) |

Every one of the 21 case names above is independently re-parsed from `RUN_TEST(...)` sites in the three
mapped suites' source text by the gate itself (never trusted from prose) and asserted to exist, via
`test_every_mapped_requirement_names_only_existing_cases`. `test_trace_eprom_v131` is asserted **excluded**
from the mapped-suite set (`test_trace_suite_is_deliberately_out_of_scope`) because its sixth `RUN_TEST`
site is `#ifdef EPROM_V131_TRACE_DUMP`-guarded, which no env defines by default (C-05) — it proves TEST-06,
not TEST-01…05, and belongs to a different section of this record entirely.

### TEST-06: the trace freeze, the fresh capture, and both gates

- **The rename** (144-03, commit `2684252`): `test/native/avr/_shared/eprom_v131_expected.h` →
  `eprom_v131_expected_prechange.h` via pure `git mv`, byte-untouched — `git hash-object` on the renamed
  path reprints Phase 138's exact blob `ca3e09f164e6e1c541ecb63d15bbebf5bce41d70`, both pre-staging and at
  `HEAD:` after the commit.
- **The fresh capture** (144-03): a new `eprom_v131_expected.h`, captured empirically from the shipped
  recorder at this phase's tip, totalling **91 / 115 / 59** entries for `0x07` / `0x08` / `0x0B` —
  validated against three stale-paste discriminators (banner totals; `strobe_overflow=0 timing_overflow=0`
  on all three; a 6-case dump-build vs. 5-case plain-build split via direct binary invocation) before a
  single line was pasted. Never `141-NEW-TRACE.md`'s stale 91/119/59.
- **The identity gate**: `firestarter/tests/test_golden_trace_identity_eprom_v131.py` — 6/6 passing,
  re-armed against the new fixture and the re-derived `tests/golden/eprom_v131_trace_inventory.json` in the
  same commit as the rename and the new capture (D-08), so the gate is never transiently RED for a reason
  that is really "the inventory hasn't caught up yet."
- **The exhaustiveness gate** (144-04, commits `9be07ba`/`6cc4795`): `firestarter/tests/test_trace_segment_exhaustiveness_v131.py`
  — 1234 lines, 11/11 passing — a six-segment state machine partitioning all 885 entries (620 pre-change +
  265 new) across both streams by set equality over `range(len(array))` plus pairwise disjointness, never a
  count sum. Full attribution table in Section 5.
- Retirement: `pio test -e native_trace_v131` goes from 3-failed/2-succeeded to **5 test cases: 5
  succeeded** — the milestone's first standing RED retired.

### TEST-07: builds, pinned and v131 env runs, both parity directions, four CI-scoped legs

- **Builds** (144-05, one cold consolidated run): `uno`, `uno328pb`, `leonardo` all build and link;
  figures in Section 2.
- **Pinned native envs** (144-05): `native` and `native_nodevtools`, each **141 test cases: 141 succeeded**,
  17 suites — the figures `check_size_baseline.py`'s `compare_native` asserts.
- **v131 env runs, by name** (144-05): `native_params_v131` **9/9**, `native_loop_v131` **79/79** (two
  suites), `native_trace_v131` **5/5, 0 failed**.
- **The CAP-03 cross-repo layout gate** (144-02, commits `52b2b97`/`68820a6`):
  `firestarter_app/tests/test_cap03_ack_layout_parity.py` — 12/12 passing — the comparison neither repo
  performed before, asserting the firmware `MSG_OK_READY` pack order against the host's `_decode_id_frame`
  offsets, including the budget read at the **computed** `4 + _vlen` / `ver_end`, never a literal index.
- **Both constants-parity directions** (144-06, on `.venv/ci-replica/bin/python` 3.11.15): present path —
  `test_revision_constants_parity.py` **14 passed**, whole host suite **1590 passed, 0 skipped**; absent
  path (genuine child process, `FIRESTARTER_FW_ROOT` at an empty, `.git`-free directory) — parity module
  **6 passed, 8 skipped** (the RESEARCH-predicted known answer, exactly), whole host suite **1540 passed, 50
  skipped**, zero `ERROR`/`E`-prefixed lines, exit 0.
- **Four CI-scoped legs** (144-06), each cited at its real `ci.yml` line (C-02, not the stale ":80–:87"
  range some earlier documents cite): `ruff check firestarter/ tests/` (**:81**, "All checks passed!"),
  `ruff format --check firestarter/ tests/` (**:84**, "135 files already formatted"),
  `python tools/check_mypy_watermark.py` (**:87**, 33 errors against a watermark of 35, exit 0),
  `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` (**:90**, 1590 passed,
  82.92% coverage). All four exit 0 on `.venv/ci-replica/bin/python` 3.11.15.

### TEST-08: measured deltas, the re-anchor, both gate verdicts

- **Measured deltas** (144-05, one cold consolidated run against the PREP-03 anchor 23954/24004/26016):
  **+870 B / +870 B / +890 B flash** on `uno` / `uno328pb` / `leonardo`, **RAM unmoved** on all three.
  Leonardo ceiling **26906 / 28672 = 93.8%**, **1766 B** headroom — watched explicitly, as TEST-08 requires,
  not discovered.
- **The re-anchor** (144-05, one commit `a594173`): all three baselines (`size_baseline.json`,
  `size_baseline_base01.json`, `size_baseline_v131.json`) rewritten to the v1.31 tip.
- **Both gate verdicts**, post-rewrite: the strict-identity mode of `check_size_baseline.py` PASSes at
  exact zero delta, and the `--policy merge05` mode PASSes at exact zero delta against the re-anchored
  `size_baseline_base01.json` — see Section 4 for the disclosure this record is obliged to make about why
  the latter now passes.

---

## 2. Cold Measurement Tables

All figures below are the **single cold consolidated run** 144-05 performed against the FINAL v1.31 tree
(D-02): `pio run -t clean -e <env>` then one uninterrupted `pio run -e <env>` per AVR target;
`rm -rf .pio/build/<env>` then `pio test -e <env>` per native env.

### 2.1 Per-target flash and RAM, against the PREP-03 anchor

| Target | Flash used/total | RAM used/total | Delta vs. PREP-03 anchor (23954/24004/26016 flash; 1573/1579/2014 RAM) |
|---|---|---|---|
| `uno` | 24824 / 32256 | 1573 / 2048 | **+870 B flash, +0 RAM** |
| `uno328pb` | 24874 / 32384 | 1579 / 2048 | **+870 B flash, +0 RAM** |
| `leonardo` | 26906 / 28672 | 2014 / 2560 | **+890 B flash, +0 RAM** |

**Leonardo ceiling:** 26906 / 28672 = **93.8%**, leaving **1766 B** headroom. RAM is unmoved on all three
targets since the PREP-03 anchor.

**Attribution of the +870/+870/+890 B growth**, from 144-05's own reconciliation, byte-identical to
`143-HOST-RECORD.md` §7.1's independent cold measurement: the parameter table finally linking
(`eprom_params_for()` gaining its first `src/` caller, Phase 140, **~+204 B**); the per-byte pulse-to-verify
loop rewrite (Phase 141); the shared `eprom_hv_route_mask()` HV-route resolver (Phase 142); and the
host-facing CAP-02/CAP-03 identity+budget ack plus the guarded `MSG_DATA_PROGRESS` emission (Phase 143).
This record's own D-14 disclosure in Section 4 depends on the +204 B figure by name.

### 2.2 Native envs, cold, each count labelled with its producing env

| Env | Cases | Suites | All passed | CI coverage |
|---|---|---|---|---|
| `native` | 141 | 17 | true | pinned, CI-covered (`build.yml`/`beta-build.yml`) |
| `native_nodevtools` | 141 | 17 | true | pinned, CI-covered |
| `native_params_v131` | 9 | 1 | true | run-by-name only, **no CI leg** |
| `native_loop_v131` | 79 | 2 (`test_loop_eprom_v131` 47 + `test_vpp_eprom_v131` 32) | true | run-by-name only, **no CI leg** |
| `native_trace_v131` | 5 | 1 | true, 0 failed | run-by-name only, **no CI leg**; retired from RED by 144-03's re-freeze |

**Labelling rule, stated plainly:** the three mapped suites' union (`test_loop_eprom_v131` 47 +
`test_vpp_eprom_v131` 32 + `test_eprom_params_v131` 9 = **88**) is the mapping gate's own non-vacuity
denominator (Section 1, TEST-01…05) — a fact about how many distinct cases exist across the suites the
mapping gate scans. `native_loop_v131`'s own per-env case count (47 + 32 = **79**) is a fact about which two
of those three suites that env's `platformio.ini` `test_filter` names. Both are correct, both are cited
throughout this record, and they are never added together — 88 and 79 answer different questions.

### 2.3 Cold warning counts for the three `*_v131` envs (obtained by grep, never by feeding either checker script a `*_v131` name — D-22)

| Env | `macro_redefinition` | `total` | Note |
|---|---|---|---|
| `native_params_v131` | 140 | 140 | new figure, recorded in `size_baseline_v131.json` for the first time (C-01) |
| `native_loop_v131` | 154 | 154 | new figure, recorded for the first time (C-01); higher than the other two because it compiles two suites |
| `native_trace_v131` | 140 | 140 | unmoved from the pre-existing record — 144-03's fixture re-freeze did not change the compiled-warning surface |

**OD-02 (RESEARCH Open Question 1), resolved without a gap:** all three counts above were obtained cleanly,
by grepping the cold build logs directly with the exact two regexes `check_build_warnings.py` uses
(`MACRO_REDEF_RE`, `WARNING_LINE_RE`) — never by invoking either checker script with a `*_v131` env name.
144-05's own plan text allowed either outcome (a clean measurement or a named gap); the outcome here is the
former.

### 2.4 Pinned envs and AVR warning watermarks, unmoved

`native` and `native_nodevtools`: **1166** total warnings each, exactly at the watermark with **zero
headroom**. All three AVR targets: `macro_redefinition = 0` (the stricter `== 0` rule). No new warning of
any kind was introduced by this phase on any target — confirmed both pre- and post-re-anchor (Section 3).

---

## 3. Verbatim Gate Verdicts

All transcripts below are lifted verbatim from `144-05-SUMMARY.md` and `144-06-SUMMARY.md`; none are
paraphrased.

### 3.1 `check_size_baseline.py`, strict identity mode

```
=== PRE-REWRITE: strict identity, default baseline (size_baseline.json) ===
FAIL:
  uno: flash_used baseline=23954 observed=24824
  uno328pb: flash_used baseline=24004 observed=24874
  leonardo: flash_used baseline=26016 observed=26906
exit=1
```

```
=== POST-REWRITE: strict identity, default baseline (size_baseline.json) ===
PASS: uno(flash=24824/32256,ram=1573/2048), uno328pb(flash=24874/32384,ram=1579/2048), leonardo(flash=26906/28672,ram=2014/2560)
exit=0
```

### 3.2 `check_size_baseline.py`, `--policy merge05` mode

```
=== PRE-REWRITE: --policy merge05, --baseline size_baseline_base01.json ===
FAIL:
  uno: flash_used baseline=23932 observed=24824 delta=+892 exceeds MERGE-05 uno-class band of 64 B
  uno328pb: flash_used baseline=23976 observed=24874 delta=+898 exceeds MERGE-05 uno-class band of 64 B
  leonardo: flash_used baseline=26072 observed=26906 delta=+834 exceeds MERGE-05 leonardo band of 0 B
exit=1
```

```
=== POST-REWRITE: --policy merge05, --baseline size_baseline_base01.json ===
PASS: uno(flash=24824/32256[+0<=64],ram=1573/2048[=]), uno328pb(flash=24874/32384[+0<=64],ram=1579/2048[=]), leonardo(flash=26906/28672[+0<=0],ram=2014/2560[=])
exit=0
```

The post-rewrite PASS above is read against the **moved anchor** — Section 4 states, in constrained terms,
exactly why this now passes.

### 3.3 `check_size_baseline.py`, native compare mode (unaffected by the re-anchor)

```
PASS: native(cases=141,suites=17), native_nodevtools(cases=141,suites=17)
exit=0
```

Identical pre- and post-rewrite — the pinned native envs' own case/suite/status facts never moved.

### 3.4 `check_build_warnings.py`, five permitted envs (unaffected by the re-anchor)

```
PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0), leonardo: macro_redefinition=0 (== 0), native: total warnings=1166 (== watermark 1166), native_nodevtools: total warnings=1166 (== watermark 1166)
exit=0
```

Identical pre- and post-rewrite.

### 3.5 Firmware pytest, whole suite

```
$ python3 -m pytest tests/ -q
312 passed in 16.49s
```

Progression across the phase, each addition attributed: 292 (Phase 143 tip) → 301 (144-01, `+9`
`test_requirement_case_mapping_v131.py`) → 301 (144-02 is host-only, `+0`) → 301 (144-03 is a fixture/inventory
rewrite, `+0` new test functions) → 312 (144-04, `+11` `test_trace_segment_exhaustiveness_v131.py`) → 312
(144-05, `+0` new test functions — four existing plants re-derived in place, two figure literals updated).

### 3.6 The identity gate and both new firmware gates

```
$ python3 -m pytest tests/test_golden_trace_identity_eprom_v131.py -q -rs
......                                                                   [100%]
6 passed in 0.05s
```

`test_requirement_case_mapping_v131.py`: **9 passed** (144-01). `test_trace_segment_exhaustiveness_v131.py`:
**11 passed** (144-04).

### 3.7 The new host gate

`test_cap03_ack_layout_parity.py`: **12 passed** (144-02), including both D-18 planted-violation legs.

### 3.8 Constants parity, both directions (verbatim, `.venv/ci-replica/bin/python` 3.11.15)

Present path:
```
$ .venv/ci-replica/bin/python -m pytest tests/test_revision_constants_parity.py -o addopts="" -q
..............                                                           [100%]
14 passed in 0.07s
```

Absent path, genuine child process, `FIRESTARTER_FW_ROOT` set to a verified-empty, `.git`-free directory:
```
$ FIRESTARTER_FW_ROOT=/tmp/tmp.TxBaflaOiC .venv/ci-replica/bin/python -m pytest \
    tests/test_revision_constants_parity.py -o addopts="" -rs -q
.sssssss...s..                                                           [100%]
6 passed, 8 skipped in 0.06s
```

Every one of the 8 skips names the probed marker path with one canonical reason string
(`firestarter firmware checkout absent (no <marker> marker)`) — never anonymous. This is exactly the
RESEARCH-predicted known answer.

### 3.9 The four `ci.yml`-scoped commands, verbatim

```
$ .venv/ci-replica/bin/ruff check firestarter/ tests/
All checks passed!

$ .venv/ci-replica/bin/ruff format --check firestarter/ tests/
135 files already formatted

$ .venv/ci-replica/bin/python tools/check_mypy_watermark.py
checked 137 source files
mypy errors: 33 (watermark: 35)
INFO: 33 errors -- 2 below watermark (35). The watermark may be lowered to 33,
but only if this run is complete: ... Lower it in the same commit as the fixes
that reduced the count -- never to make a failing gate pass.
$ echo $?
0

$ .venv/ci-replica/bin/python -m pytest tests/ -o addopts="" --cov=firestarter \
    --cov-report=term-missing --cov-fail-under=70
collected 1590 items
...
TOTAL                               5035    860    83%
Required test coverage of 70% reached. Total coverage: 82.92%
1590 passed, 1 warning in 231.06s (0:03:51)
```

The mypy INFO line inviting a lower watermark is quoted verbatim and **not acted on** — lowering the
watermark is a decision for a commit that earns it, never a byproduct of a measurement/record-writing plan.
1590 passed reconciles exactly against Phase 143's 1578 plus 144-02's 12 new tests (`1578 + 12 = 1590`);
coverage holds at 82.92%, unmoved, because the new module adds zero product-code lines to the instrumented
`firestarter/` package.

**Boundary on the fourth command, stated so it cannot be misread:** the `1590 passed` / `82.92%` figures
above were measured with the firmware sibling repo **present** (§3.8's present path), which is this
devcontainer's normal state, not GitHub Actions' state. This command is cited at `ci.yml` **:90** because
it is the identical command that step runs — never because this transcript is a claim about what that step
prints when GitHub Actions actually executes it. On the real runner, with no firmware checkout, every
`requires_fw`-gated test in this same command skips instead (§3.8's absent path measured this directly:
1540 passed, 50 skipped) — that is what every CI run experiences today, and this record does not claim
otherwise anywhere (Section 6, item 5).

---

## 4. D-14: The Re-Anchor Disclosure

> **MERGE-05 reads green because its anchor moved to v1.31, not because growth stayed inside v1.24's band.**

This sentence is mandatory and constrained (`144-CONTEXT.md` D-14): an undisclosed re-anchor is precisely
the overclaim Phase 146's claim gate exists to catch, and stating it plainly here — rather than letting
Section 3.2's PASS output speak for itself — is this milestone declining to commit its own anti-pattern.

**What actually happened, in order:** Phase 141 accepted MERGE-05 as RED against its original v1.24 anchor
(**F-141-01**, the milestone's own recorded finding: the uno-class overrun and the leonardo overrun were
both operator-accepted, never remediated, roughly **+204 B** of which is Phase 140's parameter table finally
linking now that `eprom_params_for()` has its first `src/` caller). Phase 142 and Phase 143 each measured
the same RED and each declined to touch it, citing F-141-01 by name and deferring reconciliation to this
phase (`142-VPP-RECORD.md` §1.5; `143-HOST-RECORD.md` §7.4, hand-off H3). This phase (144-05, D-11) is the
first to act: the operator took the trade of re-anchoring `size_baseline_base01.json` to the v1.31 tip,
which **permanently retires MERGE-05's ability to make its original v1.24 comparison** — that comparison is
not merely hidden, it cannot be repeated from this baseline again — while **keeping the forward mechanism**:
the `0 B` / `64 B` band literals are unchanged, and `MERGE05_UNO_CLASS_FLASH_BAND` is still **64**. What the
policy now measures is growth **from the v1.31 tip forward**, arming a **0 B** leonardo tripwire against
Phases 145 and 146 over the 1766 B of remaining headroom — the trade D-11 states explicitly, and the
judgement call this record hands to the operator's own review in Task 2 rather than treating as settled by
this plan alone.

The historical v1.24 content is not preserved in-tree; `size_baseline_base01.json`'s original Phase-123
`meta` fields (generated/phase/generated_by/tree_shas/note) were left untouched as the historical record of
that file's genesis, with a new `re_anchor_note` field added alongside them stating plainly that
`avr_targets` was overwritten in place and why — an edited-to-look-consistent history was rejected in favor
of git history at the pre-re-anchor blob (`b940c91655600a57ad7ef67cba723943af929daf`) being the record.

---

## 5. Trace Diff: Per-Segment Attribution (TEST-06)

`firestarter/tests/test_trace_segment_exhaustiveness_v131.py` (144-04) partitions both streams — the frozen
`eprom_v131_expected_prechange.h` (620 entries: 198+221+201) and the fresh `eprom_v131_expected.h` (265
entries: 91+115+59) — into six named segments by set equality over `range(len(array))` plus pairwise
disjointness, never a count sum. Every one of the **885** entries lands in exactly one attributed segment.

```
===== Protocol 0x07 (EPROM_V131_TRACE_PROTO_07) =====
segment           pre-change     new   delta
init                       5       5      +0
route_assert              31       4     -27
address_set               72      24     -48
pulse                     42      18     -24
verify_read               48      40      -8
teardown                    0       0      +0
TOTAL                    198      91    -107

===== Protocol 0x08 (EPROM_V131_TRACE_PROTO_08) =====
segment           pre-change     new   delta
init                       5       5      +0
route_assert              54      28     -26
address_set               72      24     -48
pulse                     42      18     -24
verify_read               48      40      -8
teardown                    0       0      +0
TOTAL                    221     115    -106

===== Protocol 0x0B (EPROM_V131_TRACE_PROTO_0B) =====
segment           pre-change     new   delta
init                       5       5      +0
route_assert              30       0     -30
address_set               76      12     -64
pulse                     42      18     -24
verify_read               48      24     -24
teardown                    0       0      +0
TOTAL                    201      59    -142
```

**Subtotals:** pre-change **620** (198+221+201), new **265** (91+115+59), grand total **885**. Every present
segment carries a named attribution from Phases 140–143:

| Segment | Attributed to |
|---|---|
| `init` | Phase 140 (`eprom_params_t.vpp_path` column, `eprom_params.cpp`) — supplies which HV route this protocol uses; Phase 142 (`eprom_hv_route_mask()`) — resolves it |
| `route_assert` | Phase 142 D-01/D-02 (as amended): the HV route mask now survives every `set_address()` call within a block, so this group latches once per block rather than once per pass |
| `address_set` | Phase 141 D-01 (the shared per-byte pulse-to-verify loop): each byte's address is latched once per byte-visit, not once per old-cadence pass |
| `pulse` | Phase 140 (`eprom_params_t` per-row pulse width) + Phase 141 D-01/D-02 (fixed-width pulse, verify, repeat) |
| `verify_read` | Phase 140 (`eprom_params_t.verify_mode` column: `VERIFY_PER_PULSE_PLUS_FINAL` / `VERIFY_PER_PULSE`) + Phase 141 D-01/D-06 (per-pulse verify plus the FF-rule's final-pass carve-out) |
| `teardown` | Phase 143 D-09/D-10 (as amended): a **successful** block deliberately leaves the HV route energised, so neither stream contains a teardown group at all — the zero-entry contribution is a named fact, not an omission |

The known-answer self-test (`test_pre_change_0x07_pulse_and_verify_counts_match_the_output_enable_toggles`):
pre-change `0x07` yields **7 pulse windows + 12 verify-read windows = 19**, matching an *independently
recounted* total of `OUTPUT_ENABLE` strobes on that array — proof the state machine is not merely
self-consistent with its own segmentation.

**Honest boundary, restated exactly as 144-04 stated it:** this gate proves the attribution is **COMPLETE**
— every one of the 885 entries lands in exactly one named segment, and every present segment names a
decision — it does **NOT** prove any single citation above is **CORRECT**. Attribution completeness is
machine-proven; attribution correctness is this record's own judgement, offered for the operator's review
at Task 2's checkpoint alongside D-14's re-anchor.

---

## 6. Non-Claims

1. **D-03's non-claim.** `overprogram_factor` is `0` on all three shipped rows (`eprom_params.cpp:46-48`),
   so the overprogram path is structurally unreachable on live data. The **arithmetic** is proven directly
   by five `test_loop03_*` cases (Section 1, TEST-03); the **in-loop wiring on a live row is NOT proven**,
   because no shipped row sets `overprogram_factor` to anything but zero —
   `test_loop04_no_live_row_emits_an_overprogram_pulse` is the case that witnesses this gap rather than
   papering over it. An end-to-end synthetic-row oracle would need a params-table substitution, reachable
   only via a seventh native env or a seam in blob-pinned `src/`; the operator chose the honest cheap
   option (flip on the pure-function proof, record the gap) over paying that cost during a verification
   phase (`144-CONTEXT.md` D-03).
2. **D-08's gap.** With a single inventory record, nothing gate-asserts
   `eprom_v131_expected_prechange.h`. Its preserved blob `ca3e09f164e6e1c541ecb63d15bbebf5bce41d70` stays
   hand-verifiable via `git rev-parse HEAD:test/native/avr/_shared/eprom_v131_expected_prechange.h` and is
   cited throughout this record, but it is **not machine-checked** by this or any other gate. No second
   inventory record is added to close this gap this phase — named as deferred work (Section 10).
3. **D-15's absence.** The three `*_v131` envs — `native_params_v131`, `native_loop_v131`,
   `native_trace_v131` — run in **no CI leg** of either repository. This is a local run-by-name obligation,
   recorded loudly, never an implied CI-coverage claim.
4. **No bench claim, and TEST-04's boundary.** No bench run happened in this phase, and nothing here is a
   claim about real silicon — Phase 145 owns that entirely. TEST-04's "disables every high-voltage route"
   clause is proven **only in the emitted control-register stream** — never behaviourally, never on real
   hardware — and this record does not narrow or widen that boundary beyond what the requirement's own text
   already says. No chip's `support_status` changed anywhere in this phase.
5. **The app's CI has no firmware checkout.** Every cross-repo parity gate — the constants-parity module and
   the new CAP-03 layout gate alike — skips there. `requires_fw` fails **OPEN** across the repo boundary by
   design (144-06's own measured absent-path figure, 50 skips across 11 distinct modules, is the direct,
   quantified proof of exactly what every CI run experiences today — not an abstract assertion).
6. **OD-02, resolved, no gap.** The cold warning counts for `native_params_v131` (140) and
   `native_loop_v131` (154) were obtained without violating D-22 — via direct grep of the cold build logs
   using the exact two regexes `check_build_warnings.py` uses, never by feeding either env name to a checker
   script (Section 2.3). Both outcomes (a clean measurement or a named gap) were acceptable under 144-05's
   own plan text; the outcome here is the former, stated plainly rather than assumed.
7. **The CAP-03 gate's own bounds-vs-layout non-claim** (144-02's module docstring, quoted): the gate
   "proves the two sides agree on LAYOUT, not on BOUNDS." The firmware clamps `_vlen` to `<= 32`
   (`src/firestarter.cpp:187-189`); the host's `_decode_id_frame` applies no upper bound of its own on the
   version-length byte and relies only on the runtime guard `ver_end <= len(params_bytes)`. That asymmetry
   is safe, not a defect, but a GREEN run of that gate must never be read as "the host independently proves
   the 32-byte ceiling too." It does not, and was not designed to.

---

## 7. Corrections Surfaced This Phase

**C-04 — `144-CONTEXT.md`'s own prose nominated a phantom pair.** `<code_context>` named, for TEST-05, "the
four `test_loop06_*` and **the two fallback cases**" — a pair that names no existing case at all. The
measured shape (`firestarter/test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp`) is **six**
fallback-adjacent cases in two families of three: `test_0x{07,08,0B}_zero_pulse_delay_takes_the_*us_fallback`
and their `test_0x{07,08,0B}_nonzero_pulse_delay_is_left_alone` negative controls (the second family is the
non-vacuity half — a fallback that fired unconditionally would pass the first three and fail these). This is
exactly the defect class D-01's own mapping gate exists to catch, and it arrived in the phase's **own input**
document before any code moved — worth stating plainly here rather than quietly fixing without comment. The
corrected six-case shape is what `_REQUIREMENT_CASES["TEST-05"]` freezes (Section 1).

**C-01 — `size_baseline_v131.json` held only one of the three v131 envs; D-13's "refresh" added two records
it never held.** `144-CONTEXT.md` D-13 spoke of `native_loop_v131` and `native_params_v131` counts that had
"gone stale," implying the file already carried them. Measured: before this phase, the file's `native_envs`
and `warnings.native` blocks held only `native`, `native_nodevtools`, `native_pinmap_provisional`, and
`native_trace_v131` — `native_loop_v131` and `native_params_v131` were **absent from both blocks**.
`141-NEW-TRACE.md` §6 recorded those two envs' counts in prose only, explicitly "never in a baseline JSON."
144-05's own `size_baseline_v131.json` rewrite is therefore a **policy change**, not a refresh of stale
data: it adds two env records the file never held, with a `c01_policy_change` meta field stating so.

---

## 8. D-18 Planted-Violation Inventory

D-18 (carried from Phases 140–143) requires every new gate leg to be seen RED on a planted violation before
its GREEN is believed — a pre-authored leg can be unreachable, so RED alone proves nothing. Ten plants
across this phase's three new gates plus one re-anchored gate, each seen RED for a locating reason and GREEN
attributed to a non-empty, real extraction:

| # | Plant | Owning plan / gate | RED — locating detail | GREEN — attributing test |
|---|---|---|---|---|
| 1 | Renamed `TEST-02` case (`test_loop01_pulse_width_never_grows_between_attempts` → `...grows`) | 144-01 / mapping gate | Names the missing case **and** `TEST-02` — never a bare "lists differ" | `test_planted_renamed_case_is_detected`, attributed to the real 88-name extraction |
| 2 | Emptied scan root | 144-01 / mapping gate | Names the hardcoded floor (88) and the observed count (0) together: `"is 0, expected >= 88"` | `test_planted_emptied_scan_root_fails_the_non_vacuity_leg` |
| 3 | Literal budget index (`_ready[13]`/`_ready[14]`) | 144-02 / CAP-03 layout gate | Names the literal indices `13`/`14` **and** the required computed offset `4 + _vlen` | `test_planted_literal_index_is_detected`, attributed to the real firmware's 9/9 pack-site extraction |
| 4 | Truncated emitted length (omits the budget's `+2`) | 144-02 / CAP-03 layout gate | Names the observed `(uint8_t)(4 + _vlen)` **and** the required `+ 2` | `test_planted_truncated_emitted_length_is_detected` |
| 5 | Unclassifiable pin (`0x40`) at `PROTO_07` index 21 | 144-04 / exhaustiveness gate | Names the array, the index (21), and the full `(kind,pin,value,us)` tuple including `0x40` | `test_planted_unclassifiable_entry_is_located`, attributed to the real 885-entry two-stream parse |
| 6 | Length-preserving delete+duplicate at `PROTO_07` indices 22–23 | 144-04 / exhaustiveness gate | Names both uncovered indices (22, 23); states explicitly that a count-only check would NOT have caught it (length unchanged at 91) | `test_planted_delete_and_duplicate_defeats_a_count_only_check` |
| 7 | `policy_uno_over_band` (re-derived, `delta=+65` over the 64 B band) | 144-05 / size-baseline re-anchor | `FAIL: uno: flash_used baseline=24824 observed=24889 delta=+65 exceeds MERGE-05 uno-class band of 64 B` | `test_policy_merge05_fires_on_uno_class_over_band` |
| 8 | `policy_leonardo_growth` (re-derived, `delta=+1` over the 0 B band) | 144-05 / size-baseline re-anchor | `FAIL: leonardo: flash_used baseline=26906 observed=26907 delta=+1 exceeds MERGE-05 leonardo band of 0 B` | `test_policy_merge05_fires_on_leonardo_growth` |
| 9 | `policy_ram_moved` (re-derived, RAM `+1 B`) | 144-05 / size-baseline re-anchor | `FAIL: uno: ram_used baseline=1573 observed=1574 delta=+1 (MERGE-05 requires ram_used unchanged)` | `test_policy_merge05_fires_on_ram_move` |
| 10 | `flash_regression` (re-derived, leonardo 26906→27418) | 144-05 / size-baseline re-anchor | `FAIL: leonardo: flash_used baseline=26906 observed=27418` | `test_planted_flash_regression_flips_checker_to_failure` |

Plants 1–6 are freshly authored legs (144-01, 144-02, 144-04); plants 7–10 are **re-derivations** of
pre-existing plants whose ground moved under them when 144-05 re-anchored the baseline — each is treated as
a genuinely new plant under D-18 (its RED transcript was captured fresh against the real checker at its new
figures before its paired test's GREEN was trusted), never assumed transitively from the old fixture having
once fired. Every RED transcript's full verbatim text lives in its owning plan's own SUMMARY under
"D-18 Evidence"; this table is the cross-plan index. **The governing principle, restated:** a pre-authored
leg can be unreachable, so a RED alone proves nothing until the same leg has also been seen to pass for the
right reason.

---

## 9. Findings Register

| ID | Finding | Owner | Disposition |
|---|---|---|---|
| F-144-01 | `firestarter/CLAUDE.md` still documents `native_loop_v131`'s total using a stale pre-Phase-142 figure (39 + 32) rather than the measured 47 + 32 = 79 (F-01). Phase 142's own `test_vpp_eprom_v131` growth was never folded back into that doc. | Phase 146 / CLOSE-04 | Named, not fixed here. |
| F-144-02 | `144-RESEARCH.md`'s F-11 census counted the non-`requires_fw` legs of `test_revision_constants_parity.py` as a single "all fixture-driven planted-violation legs" population of six. 144-06's own direct read of `@requires_fw` placement refines this into **two** populations: four are genuinely fixture/tmp-path-driven planted-violation legs, and two (`test_revision_byte_values_match_firmware_enum`, `test_command_names_dereferences_both_sdp_commands`) never touch the firmware repo at runtime and were never `requires_fw` candidates at all. The same split (2 plants + 3 self-check legs, 0 in the third population) reproduces on 144-02's `test_cap03_ack_layout_parity.py`. | This record | Corrected precision; no further action needed. |
| F-144-03 | D-08's named gap remains open: no gate asserts `eprom_v131_expected_prechange.h`. A second inventory record would close it. | Unassigned | Deferred by choice (`144-CONTEXT.md`'s own deferred list), not an oversight. |
| F-144-04 | D-15's absence is unresolved by design: none of `native_params_v131`, `native_loop_v131`, `native_trace_v131` run in any CI leg of either repository. | No v1.31 owner | v1.32 infrastructure work, deliberately out of this milestone's scope. |
| F-144-05 | D-16's absence is now measured, not merely asserted: the app's CI has no firmware checkout, and 144-06's own absent-path sweep (50 skips across 11 modules, zero errors, exit 0) is the direct, quantified proof of what every CI run experiences today. | Unassigned | Blocked on deciding which firmware ref app CI should pin (`beta` and the v1.31 branch disagree today). |
| F-144-06 | D-11's re-anchor permanently retires MERGE-05's ability to compare against v1.24. The historical v1.24 figures remain recoverable only via git history at the pre-re-anchor blob (`b940c91655600a57ad7ef67cba723943af929daf` for `size_baseline_base01.json`), never again in-tree. | None — closed, accepted trade | Named here for completeness; not an open item. |

---

## 10. Hand-Offs

| # | Item | Owner |
|---|---|---|
| H1 | The honesty ledger pairing every permitted milestone claim with its explicit non-claim, leading with the 6.25 V ceiling and the asymmetric bench coverage. | **Phase 146 / CLOSE-02** |
| H2 | The committed claim gate forbidding unqualified "datasheet-conformant" / "datasheet-correct" / "algorithm-accurate" across all closing artifacts, armed against the real files and seen to fail on a planted violation. | **Phase 146 / CLOSE-01** |
| H3 | gh#15's acceptance criteria, reconciled item by item — each marked met, met-as-corrected, or not-reachable-on-this-hardware. | **Phase 146 / CLOSE-04** |
| H4 | Phase 143's deferred `ROADMAP.md`/`PROJECT.md` prose correction (`143-HOST-RECORD.md` §6, D-01: Phase 143 is factually **not** independent of Phases 140–142, and is dual-repo, contrary to the roadmap's own framing). | **Phase 146 / CLOSE-04** |
| H5 | Reconciling `firestarter/CLAUDE.md`'s stale `native_loop_v131` total against the measured 79 (F-144-01). | **Phase 146 / CLOSE-04** |
| H6 | All bench evidence underlying TEST-01…TEST-08's algorithm and BENCH-01…03: real bar motion, a real long write surviving on physical hardware, per-run evidence, and chip-availability dispositions. Must re-flash before any bench check (BF-1 means a stale image cannot even connect). | **Phase 145** |
| H7 | The Leonardo headroom this record hands forward: 1766 B, now armed at a 0 B growth tripwire for the leonardo class via the re-anchored MERGE-05 mechanism (Section 4), against both Phase 145 and Phase 146 — D-11's stated intent. | **Phase 145 / Phase 146** |
| H8 | D-08's gap (F-144-03): a second inventory record for `eprom_v131_expected_prechange.h`, if this gap is ever closed. | Unassigned |
| H9 | F-141-11 / F-143-02 / F-143-03's whole-repo porcelain coupling in `test_flash_path_record_sync.py` and its host-side analog (`test_py32_flash_map_host.py`) — still orphaned, bit this phase too (D-20), sequenced around rather than fixed. | Unassigned |
| H10 | F-138-05 / F-143-04's uncaught `KeyError` in `check_size_baseline.py` on an unrecognized native env name — inherited, accepted, not fixed; never risked this phase (D-22). | henols |

---

## 11. Gate-State Summary — D-04

For the first time this milestone, **both** `protocol_branch_inventory.json` pins —
`src/proms/eprom.cpp` at `cedc88dc20936d0749f03572551b0621063ae930` and `src/proms/eprom_params.cpp` at
`5dffe841aeb7013f9f53e9991a6248b203ae22da` — matched `HEAD` at **every** point across this phase's six
plans, because no file under `firestarter/src/` was touched. Unlike Phases 141, 142, and 143 — each of which
had to move one or both pins at least once — Phase 144 can say this plainly.

**The check that proves it:** `firestarter/tests/test_protocol_branch_inventory.py`, confirmed passing
throughout — 7/7 (144-03's own direct run) and as part of the 20-passed bundle alongside
`test_golden_trace_identity_eprom_v131.py` and `test_checker_convention.py` (144-01's and 144-04's own
whole-repo confirmations). Independently, every plan that touched the firestarter working tree recorded its
own zero-diff proof against `src/`: 144-01 (`git diff --stat HEAD~2 -- src/` → 0 lines), 144-03
(`git show --stat --name-only HEAD | grep -c "^firestarter\|^src/"` → 0), 144-04
(`git diff --stat HEAD -- src/` → empty), and 144-05 (`git diff HEAD~1 --stat -- scripts/check_size_baseline.py
scripts/check_build_warnings.py src/` → empty). 144-06 touched neither sub-repo's tracked state at all
(`git -C firestarter status --porcelain` → 0 throughout). D-04's own consequence — "a plan that finds itself
needing an `src/` edit must stop and report, not absorb it" — was never triggered.

---

*Phase: 144-tests-build-verification — Plan 07*
*Recorded: 2026-08-14, from this plan's own Task 1, citing the six prior plans' committed SUMMARY.md
artifacts (`144-01-SUMMARY.md` through `144-06-SUMMARY.md`), `144-CONTEXT.md`, `144-RESEARCH.md`, and
`143-HOST-RECORD.md` for the structural precedent.*
