---
phase: 140
slug: parameter-table
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-09
---

# Phase 140 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `140-RESEARCH.md` § Validation Architecture. Measured figures in that
> section are cold-build measurements taken during research — re-measure, do not assume.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Unity 2.6.1 (firmware native C++, via PlatformIO `test_framework = unity`) · pytest (firmware gates + host gates) |
| **Config file** | `firestarter/platformio.ini` · `firestarter_app/pyproject.toml` (`addopts = -ra -q`) · no `conftest.py` anywhere in `firestarter/tests/` (house rule — every module resolves its own paths) |
| **Quick run command** | `cd /workspaces/firestarter && python3 -m pytest tests/ -q` (baseline **227 passed**) |
| **Full suite command** | `cd /workspaces/firestarter && pio test -e native && pio test -e native_nodevtools && pio test -e native_trace_v131 && pio test -e native_params_v131 && python3 -m pytest tests/ -q` then `cd /workspaces/firestarter_app && python3 -m pytest tests/ -o addopts="" -q` (baseline **1539 passed**) |
| **Estimated runtime** | ~60 s quick · ~10 min full · cold size/warning capture needs a ≥540 s timeout per env |

**Baselines that must not move** (regression pins, not new coverage):

| Pin | Expected |
|-----|----------|
| `pio test -e native` | 141 cases / 17 suites |
| `pio test -e native_nodevtools` | 141 cases / 17 suites |
| `pio test -e native_trace_v131` | 5 cases / 1 suite, GREEN (D-10 frozen baseline) |
| `check_build_warnings.py` on `native` / `native_nodevtools` | exactly **1166** each — **zero headroom** at the watermark |
| `check_size_baseline.py --policy merge05` | inside the MERGE-05 band, RAM delta exactly 0 |

> **Cold-measurement rule:** `rm -rf .pio/build/<env>` then a **single** `pio run`/`pio test`
> invocation. Warm figures under-count (native warm 998 vs cold 1166) and will produce a false pass.

> **Warning-watermark trap (F-140-01):** any TU that includes both `<Arduino.h>` and the
> `avr/pgmspace.h` shim emits exactly 14 ArduinoFake macro-redefinition warnings. With the watermark
> sitting *at* 1166 and `build_src_filter = +<proms/>` shared by all five native envs, a
> conventionally-styled `src/proms/eprom_params.cpp` turns a live gate RED. Follow the
> `src/proms/not_implemented.cpp` shape (includes `firestarter.h`, **not** `<Arduino.h>`) — verified
> to emit zero such warnings.

---

## Sampling Rate

- **After every task commit:** `python3 -m pytest tests/ -q` in whichever repo the task touched
  (firmware 227 → 227+N; app 1539 → 1539+N), plus `pio test -e native_params_v131` for tasks
  touching that suite.
- **After every plan wave:** the full suite command above (both repos).
- **Before `/gsd-verify-work`:** full suite green, **plus** a cold size/warning capture feeding
  `check_size_baseline.py --policy merge05` and `check_build_warnings.py`, **plus** every new gate
  seen RED on a planted violation and then GREEN (D-15).
- **Max feedback latency:** ~60 s (quick) / ~10 min (wave).

---

## Per-Task Verification Map

Task IDs are assigned by the planner; this map is keyed by requirement and artifact so the planner
can attach each row to the task that creates it.

| Artifact / Behavior | Plan | Wave | Requirement | Threat Ref | Test Type | Automated Command | File Exists | Status |
|---------------------|------|------|-------------|------------|-----------|-------------------|-------------|--------|
| Three rows keyed `0x07`/`0x08`/`0x0B`, six columns each; each protocol resolves to its own distinct row | TBD | 1 | TABLE-01 | — | native unit | `pio test -e native_params_v131` | ❌ W0 | ⬜ pending |
| Struct field-name list is exactly the frozen six; row set is exactly three | TBD | 2 | TABLE-01 | — | committed gate (pytest, fw CI) | `python3 -m pytest tests/test_eprom_params_citations.py -q` | ❌ W0 | ⬜ pending |
| No pulse-width column exists anywhere in the table | TBD | 2 | TABLE-02 | — | committed gate | same module — assert no field matches `(?i)(pulse_(width\|delay\|us)\|fallback_pulse)`; assert the only field containing "pulse" is exactly `max_pulses` | ❌ W0 | ⬜ pending |
| Write path still reads `handle->pulse_delay` | TBD | 1 | TABLE-02 | — | behavioural (frozen trace) | `pio test -e native_trace_v131` — frozen arrays encode the 100/500 µs cadence | ✅ | ⬜ pending |
| `pulse_delay == 0` ⇒ 1000/100/500 µs per protocol, **exercised** (3 positive cases) | TBD | 1 | TABLE-03 | — | native unit | `pio test -e native_params_v131` | ❌ W0 | ⬜ pending |
| `pulse_delay != 0` ⇒ untouched (3 negative controls, non-vacuity) | TBD | 1 | TABLE-03 | — | native unit | same suite | ❌ W0 | ⬜ pending |
| Every `(row, column)` cell has exactly one sidecar citation; no citation for a non-existent cell; `cells_scanned == 18` | TBD | 2 | TABLE-04 | — | committed gate | `python3 -m pytest tests/test_eprom_params_citations.py -q` | ❌ W0 | ⬜ pending |
| Each citation well-formed: (family + part + doc-number + revision/date + section) **and** the literal D-09 scope sentence, **or** the exact `"no datasheet basis — reasoned from "` prefix | TBD | 2 | TABLE-04 | — | committed gate | same module | ❌ W0 | ⬜ pending |
| No second firmware algorithm selector — protocol-branch-site inventory in `src/proms/eprom.cpp` matches the pin, with the pre-existing-routing allowlist | TBD | 2 | TABLE-05 | — | committed gate (pytest, fw CI) | `python3 -m pytest tests/test_protocol_branch_inventory.py -q` | ❌ W0 | ⬜ pending |
| No new `chip_database.json` field — union of keys at top level / `programming` / `electrical` **with per-key occurrence counts** equals the frozen inventory | TBD | 2 | TABLE-05 | — | committed gate (pytest, app CI) | `cd /workspaces/firestarter_app && python3 -m pytest tests/test_chip_database_field_inventory.py -q` | ❌ W0 | ⬜ pending |
| Neither pinned native env moved | TBD | 3 | all | — | regression | `pio test -e native` → 141/17; `pio test -e native_nodevtools` → 141/17 | ✅ | ⬜ pending |
| AVR flash/RAM inside MERGE-05 band, RAM delta exactly 0 | TBD | 3 | all | — | cold measurement + gate | `python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log uno=… …` | ✅ | ⬜ pending |
| Native warning watermark unmoved | TBD | 3 | all | — | cold measurement + gate | `python3 scripts/check_build_warnings.py` on `native` / `native_nodevtools` — expect exactly 1166 each | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**Non-vacuity obligation (D-15):** each of the three new gates must be **seen RED** on a planted
violation before its GREEN is believed, and the RED output captured verbatim in the plan's SUMMARY.
A gate authored before the content it checks can be unreachable — RED proves nothing until it has
also been seen to pass for the right reason.

---

## Wave 0 Requirements

- [ ] `firestarter/include/eprom_params.h` + `firestarter/src/proms/eprom_params.cpp` — the artifact
      every other item asserts against (TABLE-01/02); **must not** include `<Arduino.h>`
- [ ] `firestarter/test/native/avr/test_eprom_params_v131/{host_stubs.cpp,test_eprom_params_v131.cpp}`
      — covers TABLE-03 and TABLE-01 row resolution
- [ ] `firestarter/platformio.ini` — `[env:native_params_v131]` (the suite is invisible until it
      appears in a positive allowlist)
- [ ] `firestarter/tests/golden/eprom_params_citations.json` — the D-14 sidecar (18 cells)
- [ ] `firestarter/tests/test_eprom_params_citations.py` — TABLE-04 + TABLE-01/02 structural gate
- [ ] `firestarter/tests/golden/protocol_branch_inventory.json` — the D-13 pin (4 sites + allowlist)
- [ ] `firestarter/tests/test_protocol_branch_inventory.py` — TABLE-05 firmware half
- [ ] `firestarter_app/tests/golden/chip_database_field_inventory.json` — frozen key set + counts
- [ ] `firestarter_app/tests/test_chip_database_field_inventory.py` — TABLE-05 DB half
- [ ] Planted-violation fixtures/runs for all three new gates (D-15)
- [ ] Framework install: **none needed**

**Frozen `chip_database.json` inventory** (746 chips, 59 manufacturers) — pin the **counts**, not
just the names; a field added to a subset would otherwise slip past a names-only assertion:

| Level | Keys → occurrence count |
|---|---|
| top level | `electrical` 746, `part_number` 746, `pinout` 746, `programming` 746, `support_status` 746, `unsupported_reason` 10, `datasheet` 2, `provenance` 2, `source` 2, `verification_note` 2, `verification_status` 2 |
| `programming` | `algorithm` 746, `chip_id_check` 746, `chip_id_value` 746, `pulse_duration` 746, `infoic_page_size_raw` 744, `protect_off_before` 744, `protect_on_after` 744, `page_size` 2 |
| `electrical` | `pin_count` 746, `size_bytes` 746, `type` 746, `vcc` 746, `vdd` 746, `vpp` 746, `vpp_mv` 746 |
| 27C protocol counts | `algorithm` 7 → **170**, 8 → **127**, 11 → **32** |

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `pio test -e native_params_v131` result | TABLE-01, TABLE-03 | **The env does not run in CI.** Neither `build.yml` nor `beta-build.yml` invokes any env beyond `native` and `native_nodevtools` (F-140-11). | Run by name locally; record pass/fail **counts** in the phase record (D-11). Same obligation applies to `native_trace_v131`. |
| Cold size / warning capture | all | Warm builds under-count; CI does not do a cold capture for these envs | `rm -rf .pio/build/<env>` then a single `pio run -e uno\|uno328pb\|leonardo` at ≥540 s timeout, feeding the two check scripts |
| `0x07`'s `overprogram_factor` value | TABLE-03 (data) | **Not validatable by any test in this phase** — the table is unreferenced by `src/` (D-10). It is a data-correctness question settled by attribution, not assertion. | **Operator-decided this session: `0` (see Locked Decisions below).** Verification is that the citation records the decision and its basis, not that a test asserts the number. |

**Explicitly NOT verifiable at any level — stated rather than implied:**

- **No bench oracle exists for TABLE-03.** 0 of 329 shipped 27C chips yields `pulse_delay == 0`
  (F-140-04). A bench run cannot reach the fallback; claiming bench coverage for it would be false.
  Phase 145's bench work covers the *loop*, not this branch. The native suite is the **only** oracle.
- **`check_size_baseline.py` and `check_build_warnings.py` are blind to the new env** (F-138-05:
  uncaught `KeyError` → exit 1; no baseline entry → exit 2). **Do not** pass `native_params_v131`
  to either script.
- **The 6.25 V program-VCC and the datasheets' raised-VCC verify passes are unreachable on this
  hardware** — unverifiable at any level. This is the milestone's evidence ceiling and the reason
  D-02 forbids a verify-VCC column.

---

## Locked Decisions Carried Into Planning

- **`0x07 overprogram_factor = 0`** — operator-delegated, decided 2026-08-09. Basis: the firmware
  applies no overprogram pulse on any protocol today (`src/proms/eprom.cpp:161-178` is retry
  escalation, not an Intel 3N margin pulse), so `0` is behaviour-preserving while `3` would be an
  unvalidated behaviour change to all 170 chips in the row; and all three `0x07` datasheets read
  (Winbond W27C512, ST M27C512, Microchip 27C512A — 113 of 170 chips) specify no overprogram.
  The 22 Intel-family parts that genuinely want a 3N pulse are recorded as a **named, scoped
  divergence** from PROJECT.md's throughput table, plus a follow-up candidate — serving them
  correctly requires splitting `0x07`, which this phase's "no second dispatch key" constraint forbids.
- **`0x08 overprogram_factor = 0`** — settled from primary datasheets (D-06 tie-break, prose wins):
  ST M27C1001 states verbatim *"No overprogram pulse is applied since the verify in Margin mode
  provides necessary margin"*; AMD Am27C020 Flashrite and Winbond W27C020 flowcharts have no
  overprogram step.
- **`overprogram_cap_us` stays in the table** even though it is inert on every row — TABLE-01 names
  the column explicitly. Cite it as reasoned + explicitly inert.
- **Citation gate lives in the firmware repo** — co-located with what it checks, CI-run, no
  cross-repo seam.
- **Datasheet PDFs are not committed** — citations are self-describing (vendor, part, document
  number, revision/date, section/figure) with the recovery command recorded in the sidecar header.

**Carried forward, not this phase's to fix:** the justification sentence published on gh#15 for
`energy_cap_us = 50000` ("100 × 500 µs is the classic 2716 *total* programming time") is factually
wrong — the TI TMS 2516 datasheet's total for all bits is 100 seconds. The **value** has a genuine
primary basis (`t_w(PR)` = 45/**50**/55 ms); the **reason** does not. Phase 146 / CLOSE-04 must
reconcile.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s (quick) / 10 min (wave)
- [ ] Each of the 3 new gates seen RED on a planted violation, RED output captured verbatim
- [ ] `native_params_v131` and `native_trace_v131` counts recorded in the phase record (D-11)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
