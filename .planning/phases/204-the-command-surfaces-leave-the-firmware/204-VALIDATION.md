---
phase: "204"
slug: "the-command-surfaces-leave-the-firmware"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-21"
---

# Phase 204 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded by plan-phase from `204-RESEARCH.md` § Validation Architecture. The per-task map below is
> filled by the planner once task IDs exist; the infrastructure and sampling rows are measured, not
> assumed (baselines run 2026-09-21 against `firestarter_fw` HEAD `e5842d8`).

---

## Test Infrastructure

Three trees, three frameworks. A task that touches firmware source must satisfy the firmware
columns; a task that touches the host app must satisfy the host column.

| Property | Firmware — native (tree 1) | Firmware — source-scan (tree 2) | Host app |
|----------|----------------------------|----------------------------------|----------|
| **Framework** | PlatformIO + Unity, `platform = native` | pytest, stdlib-only, **no `conftest.py`** (house rule) | pytest with `conftest.py`, `addopts = -ra -q` |
| **Config file** | `firestarter_fw/platformio.ini` — `[native_base]` holds the single `test_filter` and `-I` list | none | `firestarter_app/pyproject.toml` |
| **Quick run command** | `pio test -e native -f "*<touched suite>*"` | `pytest tests/ -q -o addopts="" -p no:cacheprovider` | `.venv311/bin/python -m pytest tests/<touched> -o addopts="" -q` |
| **Full suite command** | `pio test -e native` **and** `pio test -e native_nodevtools` | `pytest tests/ -v` | `.venv311/bin/python -m pytest tests/ -o addopts="" -q` on **Python 3.11** |
| **Estimated runtime** | ~58 s full (~2 s per filtered suite) | ~6 s | ~30 s |

**Measured baselines (unmodified tree, 2026-09-21):**

- `pio test -e native` → **19 suites, 237 cases, 237 succeeded, 57.9 s, exit 0** (PlatformIO 6.2.0)
- `pytest tests/` in a real git working tree → green (the 11 failures seen during research are
  artifacts of a non-git scratch copy, not defects)
- The firmware phase gate is the four `build.yml` steps **in order**: `pio test -e native`,
  `pio test -e native_nodevtools`, `pytest tests/ -v`, `pio run`.

**Environment facts that bind commands:**

- Python **3.11 is not installed** by default here (3.12.14 default, 3.13.5 present). The host suite
  must run on 3.11 — `uv python install 3.11` works, but `UV_CACHE_DIR` must be redirected because
  `~/.cache/uv` is unwritable, and `uv venv` produces a venv **without pip**.
- `grep --no-ignore` **silently returns zero matches** in this devcontainer (`grep` is a bash
  function wrapping ugrep 7.8.4, which rejects the flag; with `2>/dev/null | wc -l` you get `0` and
  exit `0`). No verify command may depend on it.
- `scripts/baseline/size_baseline.json` and `check_size_baseline.py` are cited by four modules but
  **do not exist**. The flash reclaim has no automated gate and must be measured by hand.

---

## Sampling Rate

- **After every task commit:** `pytest tests/ -q -o addopts="" -p no:cacheprovider` in
  `firestarter_fw` (~6 s), plus `pio test -e native -f "*<touched suite>*"`
- **After every plan wave:** all four firmware `build.yml` legs in order, plus the host suite on
  Python 3.11
- **Before `/gsd-verify-work`:** all four firmware legs green, host suite green on 3.11, and the
  bench matrix B0–B7 recorded
- **Max feedback latency:** ~6 s (source-scan) / ~58 s (full native)

---

## Per-Task Verification Map

*Filled by the planner — task IDs do not exist until PLAN.md files are written. The requirement →
behavior → command rows below are the measured input for that mapping; every one of them must land
on at least one task.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | FWCMD-01 | — | ordinals 4/6 absent from dispatch switch, `is_memory_cmd`, `configure_memory` | source-scan | `pytest tests/test_<new>_source_contract.py -q -o addopts=""` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | FWCMD-01 | — | `is_memory_cmd` admits exactly seven values | unit (native) | `pio test -e native -f "*test_cmd_admission*"` | ✅ (re-anchor 9→7) | ⬜ pending |
| TBD | TBD | TBD | FWCMD-02 | — | both wrappers and their declarations gone | source-scan | `pytest tests/test_boolean_convention_source_contract_v133.py -q -o addopts=""` (re-anchor 9→7) | ✅ (re-anchor) | ⬜ pending |
| TBD | TBD | TBD | FWCMD-03 | — | reserved-gap record present on both ladders | source-scan | leg asserting both gaps + comment text in `firestarter.h` and `constants.py` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | FWCMD-04 | — | `eprom.cpp` still calls `memory_verify_execute` for `VERIFY_PER_PULSE_PLUS_FINAL` | source-scan, **planted RED must be seen** | `pytest tests/test_<new>_source_contract.py -q -o addopts=""` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | FWCMD-05 | — | `memory_verify_execute` raises `MSG_ERR_VERIFY` (0xAF) on mismatch | unit (native), id-asserting | `pio test -e native -f "*test_verify_ids*"` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | FWCMD-05 | — | `eeprom28c_verify_page_readback` raises 0xAF (driven via `eeprom28c_write_execute` — it is `static`) | unit (native), id-asserting | `pio test -e native -f "*test_verify_ids*"` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | FWCMD-05 | — | `flash_util_verify_operation` raises `MSG_ERR_OP_TIMEOUT` (0xB7), **not** 0xAF | unit (native), needs advancing `millis()` | `pio test -e native -f "*test_verify_ids*"` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | FWCMD-05 | — | per-pulse budget exits raise 0xBD / 0xBE | unit (native), id-asserting | `pio test -e native -f "*test_verify_ids*"` | ❌ W0 (path driven by `test_val_eprom`; the **id** assertion is new) | ⬜ pending |
| TBD | TBD | TBD | FWCMD-06 | T-204-refusal | retired ordinal → explicit refusal, no hardware effect, no hang | **manual (bench)** — `firestarter.cpp` / `eprom_operations.cpp` are outside `build_src_filter`, so no native test reaches the dispatch switch | bench B5/B6/B7 | n/a | ⬜ pending |
| TBD | TBD | TBD | REL-02 | — | post-204 host works against pre-204 firmware | **manual (bench)** | bench B2 | n/a | ⬜ pending |
| TBD | TBD | TBD | REL-03 | — | pre-204 host refused by post-204 firmware, chip content intact | **manual (bench)** | bench B5–B7 | n/a | ⬜ pending |
| TBD | TBD | TBD | criterion 6 | — | `protocol_branch_inventory.json` golden re-derived and diffed field-by-field on `line` | source-scan | `pytest tests/test_protocol_branch_inventory.py -q -o addopts=""` (re-anchor `[70]`→`[67]` + blob SHA) | ✅ (re-anchor) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter_fw/tests/test_<name>_source_contract.py` — FWCMD-04's gate (the eighth
      source-scan module). Needs a **seen** planted RED before it counts.
- [ ] `firestarter_fw/test/native/avr/test_verify_ids/` (name at planner discretion) — the FWCMD-05
      id assertions: `test_verify_ids.cpp` + `host_stubs.cpp` + `avr/pgmspace.h` shim.
- [ ] `firestarter_fw/platformio.ini` — **one** `test_filter` line and **one** `-I` line added to
      `[native_base]`.
- [ ] Re-anchors (edits, not new files): `test_cmd_admission.cpp` (9→7 + truth table);
      `test_configure_memory.cpp` (drop `CMD_VERIFY` **and** the literal `c < 3`; dispose of Case
      group 5's blank arm); `test_val_eprom.cpp` (:387 and :478 — :478 null-derefs);
      `test_val_nor_unlock.cpp:132`; `test_val_eeprom28c.cpp:170`;
      `test_blank_check_region_source_contract.py` (6→1);
      `test_boolean_convention_source_contract_v133.py` (9→7);
      `test_protocol_branch_inventory.py` (`[70]`→`[67]`) and its golden (blob SHA + 20 line
      shifts); and the three `test_eprom_operations.py` import sites in `firestarter_app`.

---

## Manual-Only Verifications

`firestarter.cpp` and `eprom_operations.cpp` sit outside `build_src_filter`, so **no native test can
reach the dispatch switch**. Every FWCMD-06 / REL-02 / REL-03 behavior is therefore bench-only by
construction, not by choice.

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `3.1.0b1` host performs `verify` and `blank` correctly against pre-`3.1.0` firmware | REL-02 | needs two real artifact versions on real hardware | bench B2: flash pre-204 firmware, run post-204 host `verify` + `blank`, record both outcomes |
| pre-`3.1.0` host against `3.1.0b1` firmware gets an actionable refusal, no hardware side effect, no hang | REL-03, FWCMD-06 | the refusal path is in a translation unit no native test links | bench B5–B7: flash post-204 firmware, drive `3.0.0b49` host `verify` then `blank`, capture the coded refusal and confirm chip content unchanged |
| `pio run -t upload` reaches the attached board from this devcontainer | (precondition for all bench legs) | USB passthrough is recorded as working but **no upload has been attempted** | bench B0: flash once and round-trip a read **before** the B1–B7 matrix is designed around it |
| Flash size reclaim | FWCMD-01/02 side effect | `scripts/baseline/size_baseline.json` and `check_size_baseline.py` do not exist — no automated gate | measure `pio run` output by hand, before and after |

**Bench rig:** `/dev/ttyACM0` = USB `2341:8036 Arduino Leonardo`, the only serial device present.
The Uno-class gap is physically real for this phase — D-10 confirmed.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
