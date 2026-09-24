---
phase: "204"
slug: "the-command-surfaces-leave-the-firmware"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
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

*Filled by the planner 2026-09-21, against the five PLAN.md files. Every requirement → behavior row
the seed carried lands on at least one task. Two command-level corrections were measured while
planning and are reflected below: the firmware `tests/` tree must be driven through
`/usr/local/py-utils/bin/pytest` (a bare `python3 -m pytest` fails with no module named pytest), and
`firestarter_app/.venv311` held a DANGLING interpreter symlink into a deleted scratch directory, so
every host command was unrunnable until 204-01 task 1 rebuilds it.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-T1 | 204-01 | 1 | FWCMD-05 | — | FWCMD-05 and ROADMAP criterion 3 name all four real ids; the host 3.11 interpreter is runnable | source-scan + env | one **region-scoped** probe asserting all four ids inside the `FWCMD-05` bullet and inside Phase 204 criterion 3, plus the `.venv311` interpreter probe | ✅ | ✅ green |
| 01-T2 | 204-01 | 1 | FWCMD-01, FWCMD-02, FWCMD-03 | T-204-01, T-204-02 | ordinal 6 absent from ladder, admission predicate, dispatch switch, wrapper, declaration and `configure_memory`; host ladder mirrors | source-scan + unit (native) | `pio test -e native`; `pio test -e native_nodevtools`; `/usr/local/py-utils/bin/pytest tests/ -o addopts="" -p no:cacheprovider -q`; the firmware and host absence probes | ✅ (re-anchor 9→8 on two counts) | ✅ green |
| 01-T2b | 204-01 | 1 | REL-03 | T-204-SC | blocking human gate before the pinned `3.0.0b49` install | checkpoint | n/a — `checkpoint:human-verify`, `gate="blocking-human"` | n/a | ✅ closed — human "approved" (204-01-SUMMARY) |
| 01-T3 | 204-01 | 1 | FWCMD-06, REL-03 | T-204-05, T-204-SC | upload path proven; ordinal 6 refused while ordinal 4 is still SERVED — a two-sided control | **bench (automated under D-10 standing permission)** | `pio run -e leonardo -t upload`; the rig probe; `cmp tracer-pre.bin tracer-post.bin` | ❌ produces `204-BENCH-TRACER.md` | ✅ recorded — `204-BENCH-TRACER.md` |
| 02-T1 | 204-02 | 2 | FWCMD-04 | T-204-07, T-204-08 | `eprom.cpp` still calls `memory_verify_execute` INSIDE the `VERIFY_PER_PULSE_PLUS_FINAL` arm, brace-matched | source-scan, **planted RED seen twice** | `/usr/local/py-utils/bin/pytest tests/test_verify_survival_source_contract.py -o addopts="" -p no:cacheprovider -v` | ❌ W0 → created here | ✅ green — planted RED re-seen 2026-09-24 |
| 02-T2 | 204-02 | 2 | FWCMD-05 | T-204-09, T-204-10 | `memory_verify_execute` raises 0xAF; `flash_util_verify_operation` raises 0xB7 and NOT 0xAF | unit (native), id-asserting, advancing `millis()` | `pio test -e native -f "*test_verify_error_ids*"` and the same under `native_nodevtools` | ❌ W0 → created here | ✅ green |
| 02-T3 | 204-02 | 2 | FWCMD-05 | T-204-09 | `eeprom28c_verify_page_readback` raises 0xAF via `eeprom28c_write_execute`; budget exits raise 0xBD / 0xBE | unit (native), id-asserting | `pio test -e native -f "*test_verify_error_ids*" -v` | ❌ W0 → created here | ✅ green |
| 03-T1 | 204-03 | 3 | FWCMD-01 | T-204-16 | both command-keyed branches and the deferred emit-and-ack block collapsed, behaviour preserved for write-init and erase-end | unit (native) + source-scan | `pio test -e native -f "*test_val_eprom*" -v`; all four CI legs | ✅ | ✅ green |
| 03-T2 | 204-03 | 3 | FWCMD-01, criterion 6 | T-204-14, T-204-15 | five `configure_*` arms gone; census gate 6→1; golden re-derived and positionally verified | source-scan + golden diff | `/usr/local/py-utils/bin/pytest tests/test_blank_check_region_source_contract.py tests/test_protocol_branch_inventory.py -o addopts="" -p no:cacheprovider -v` plus the field-by-field golden probe | ✅ (re-anchor 6→1, `[70]`→`[67]`, blob sha) | ✅ green — blank-check census module retired by 205 (`1cf1b22`) |
| 03-T3 | 204-03 | 3 | FWCMD-01, FWCMD-02, FWCMD-03 | T-204-12, T-204-13 | both ordinals absent everywhere; `is_memory_cmd` admits exactly seven; both ladders carry the reserved record | source-scan + unit (native) | `/usr/local/py-utils/bin/pytest tests/test_verify_survival_source_contract.py -o addopts="" -p no:cacheprovider -v`; `pio test -e native`; the host ladder probe | ✅ (re-anchor 8→7 on two counts) + ❌ four new absence legs | ✅ green |
| 04-T1 | 204-04 | 4 | FWCMD-02 | T-204-18, T-204-19 | both orphaned debug ids kept and annotated; codegen output byte-identical | codegen diff | `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` plus two `diff -u` regenerations | ✅ | ✅ green |
| 04-T2 | 204-04 | 4 | FWCMD-03 | T-204-20 | no firmware documentation names a retired ordinal; the fabricated INV-05 test citation repaired | source-scan | the documentation probes plus `/usr/local/py-utils/bin/pytest tests/ -o addopts="" -p no:cacheprovider -q` | ✅ | ✅ green |
| 04-T3 | 204-04 | 4 | FWCMD-03 | — | CMP-F1 carries the forward-compatibility finding; the roadmap nomination corrected in place | source-scan | the CMP-F1 and ROADMAP probes plus the completed-requirement-count invariant | ✅ | ✅ green |
| 05-T1 | 204-05 | 5 | REL-02 | T-204-26, T-204-28 | pre-204 firmware built from its own commit and flashed; part baselined non-blank at 65536 bytes | **bench (automated)** | the rig probe; `pio run -e leonardo -t upload`; the `pre.bin` size and non-blank probes | ❌ produces `204-BENCH-MATRIX.md` | ✅ recorded — `204-BENCH-MATRIX.md` |
| 05-T2 | 204-05 | 5 | REL-02 | T-204-24 | post-204 host `verify` and `blank` correct against pre-204 firmware, no unknown-command line | **bench (automated)** | `timeout 300 .venv311/bin/firestarter verify …`; `timeout 300 .venv311/bin/firestarter blank …`; `cmp pre.bin mid.bin`; `pio run -e uno -e uno328pb -e leonardo` | n/a | ✅ recorded — `204-BENCH-MATRIX.md` |
| 05-T3 | 204-05 | 5 | FWCMD-06, REL-03 | T-204-23, T-204-24, T-204-25, T-204-27 | both ordinals refused from the published `3.0.0b49` host; three whole-device reads share one digest | **bench (automated)** | the two `timeout 300 … firestarter` refusal legs; `cmp pre.bin post.bin` and `cmp mid.bin post.bin`; the three-digest probe | n/a | ✅ recorded — `204-BENCH-MATRIX.md` |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Resolved by the planner 2026-09-21. Names fixed, owners assigned.

- [x] **Host test interpreter (NEW, not in the seed).** `firestarter_app/.venv311/bin/python` is a
      DANGLING symlink into a deleted session scratch directory, so every host verify command
      inherited from Phase 203 is unrunnable. Rebuilt in **204-01 task 1** with
      `uv venv --python 3.11` plus `uv pip install --python … -e '/workspaces/firestarter_app[test]'`,
      with `UV_CACHE_DIR` redirected because `~/.cache/uv` is not writable. Python 3.11.16 is already
      installed durably under `$HOME/.local/share/uv/python`.
- [x] `firestarter_fw/tests/test_verify_survival_source_contract.py` — FWCMD-04's gate, the eighth
      source-scan module. Created in **204-02 task 1** with a **seen** planted RED for BOTH the
      deleted-call and the moved-call violation shapes. Extended in **204-03 task 3** with the
      FWCMD-01 / FWCMD-03 absence legs, whose RED is seen against the pre-deletion tree.
- [x] `firestarter_fw/test/native/avr/test_verify_error_ids/` — the FWCMD-05 id assertions.
      `test_verify_error_ids.cpp` + `host_stubs.cpp`, created in **204-02 task 2** (the two
      independent ids) and completed in **204-02 task 3** (the page read-back and the two budget
      exits). An `avr/pgmspace.h` shim is added only if the link fails without one: the two closest
      analogue suites do not carry one.
- [x] `firestarter_fw/platformio.ini` — **one** `test_filter` line and **one** include line added to
      `[native_base]`, in **204-02 task 2**. Measured: two lines, not four; `firestarter_fw/CLAUDE.md`
      is stale on this point and is repaired in 204-04 task 2.
- [x] Re-anchors, split across the waves by what each one reddens, so every commit boundary is green:
      `test_boolean_convention_source_contract_v133.py` 9→8 in **204-01 task 2** and 8→7 in
      **204-03 task 3**; `test_cmd_admission.cpp` 9→8 then 8→7 in the same two tasks;
      `test_configure_memory.cpp`'s command array, name array and hard-coded loop bound in
      **204-01 task 2** and its SRAM blank arm in **204-03 task 3**;
      `test_val_eprom.cpp`'s null-dereferencing chunking test in **204-03 task 2** and its remaining
      command-field assignment in **204-03 task 3**; `test_val_nor_unlock.cpp` and
      `test_val_eeprom28c.cpp` disposed of in **204-03 task 2**;
      `test_blank_check_region_source_contract.py` 6→1, `test_protocol_branch_inventory.py`
      `[70]`→`[67]` and the golden re-derive all in **204-03 task 2**, in ONE commit with
      `src/proms/eprom.cpp`; the host `test_eprom_operations.py` import sites in **204-01 task 2**
      (both converted to integer literals at once) with the new ladder-absence leg in
      **204-03 task 3**.

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

- [x] All tasks have `<automated>` verify or Wave 0 dependencies — 15 working tasks across 5 plans, 91 `<automated>` legs, each with a stated `<fails_when>`; the one checkpoint task (204-01 task 2b) is a blocking package-legitimacy gate and carries no runnable command by design. Count re-derived from the committed blobs at `3c8e775a` (19 + 14 + 25 + 16 + 17), with the `<automated>` open, close and `<fails_when>` counts asserted equal in each file
- [x] Sampling continuity: no 3 consecutive tasks without automated verify — every task in every plan carries at least four
- [x] Wave 0 covers all MISSING references — plus one the seed did not know about: the dangling `.venv311` interpreter, now owned by 204-01 task 1
- [x] No watch-mode flags
- [x] Feedback latency < 60s — ~6 s for the firmware source-scan tree, ~2.3 s for a filtered native suite, ~58 s for the full native run (the only leg above 60 s is `pio test -e native`, run at wave boundaries rather than per task)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** planner, 2026-09-21. Bench legs are `auto` rather than manual: the operator's standing
permission (D-10) to drive and flash the attached Leonardo without asking makes every bench step a
runnable command with an observable failure signal. The seed classified them as manual because no
*native test* can reach the dispatch switch, which remains true and is why they are bench legs at
all.

---

## Validation Audit 2026-09-24

Run by `/gsd-validate-phase 204` against the live `v1.41-verification-to-host` branches:
`firestarter_fw` `4b14111` and `firestarter_app` `5302f63`. That is three phases after 204 closed,
so every row was re-measured, not read from a SUMMARY.

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

**Gates re-run for this audit:**

| Leg | Command | Result |
|-----|---------|--------|
| Firmware native | `pio test -e native` | 244/244, exit 0 |
| Firmware native, no dev tools | `pio test -e native_nodevtools` | 244/244, exit 0 |
| FWCMD-05 id suite | `pio test -e native_nodevtools -f "*test_verify_error_ids*" -v` | 8/8 PASS, including the 0xB7-not-0xAF assertion and both budget-exit ids |
| Firmware source-scan | `/usr/local/py-utils/bin/pytest tests/ -o addopts="" -p no:cacheprovider -q` | 316 passed, exit 0 |
| The three surviving 204 gates | `test_verify_survival_source_contract.py`, `test_protocol_branch_inventory.py`, `test_boolean_convention_source_contract_v133.py` | 29/29 passed |
| FWCMD-04 planted RED | delete `memory_verify_execute(handle);` from `src/proms/eprom.cpp:489`, re-run the gate | RED on `test_the_final_verify_pass_is_still_called_for_plus_final`. The file was then restored, `git diff` was empty, and the gate returned to 15/15 |
| Firmware build | `pio run -e leonardo` | SUCCESS, 23312 bytes |
| Codegen | `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` | catalog valid, 79 messages |
| Host suite, Python 3.11.16 | `.venv311/bin/python -m pytest tests/ -o addopts="" -q -p no:cacheprovider` | 2373 passed, 36 snapshots, exit 0 |
| Absence probes | `git grep` for the four retired symbols in firmware non-test sources, and for the two host constants in non-comment host code | zero hits |

**The test-count increases do not affect Phase 204.** The 2026-09-22 verification recorded 243
native tests and 2309 host tests. Phases 205–207.1 added tests since then. The 17
`test_flash_path_record_sync.py` failures that verification recorded as pre-existing no longer occur.

**One row is superseded, and no coverage is lost.** 03-T2 drove
`tests/test_blank_check_region_source_contract.py`. Phase 205 commit `1cf1b22` deleted that module
together with the four blank-check call sites it counted. The guarantee now lives in
`test_verify_survival_source_contract.py::test_the_blank_check_machinery_is_absent` and
`::test_no_write_init_body_performs_a_blank_check`, and both pass.

**Bench rows (01-T3, 05-T1, 05-T2, 05-T3) were not re-run.** Each one observed a specific pair of
artefact versions: pre-204 firmware `e5842d8` and the published `3.0.0b49` wheel. The firmware on
the branch is now `3.1.0b1`. Re-flashing would observe a different pair, not repeat the recorded
observation. Their evidence is the transcripts in `204-BENCH-TRACER.md` and `204-BENCH-MATRIX.md`,
and the Manual-Only table above explains why they are bench-only. The chip-identity item
(`WINDOWS.md` entry 3, Chip ID `0x1818`) remains open, as it was at verification.

