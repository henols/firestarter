---
phase: "205"
slug: "the-pre-flights-leave-the-firmware"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: true
wave_0_complete: false
created: "2026-09-22"
---

# Phase 205 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded by plan-phase from `205-RESEARCH.md` § Validation Architecture. Every runtime and every
> baseline below was **measured on 2026-09-22** against `firestarter_fw` HEAD `24e3fdf` and
> `firestarter_app` HEAD `2a17fd7`, both clean — none is an estimate. The per-task map is filled by
> the planner once task IDs exist; `nyquist_compliant` flips to `true` when that map is complete and
> the sign-off checklist passes.

---

## Test Infrastructure

Three trees, three frameworks. `firestarter_fw` has two python-visible suites; the host app is the
third. A task that edits firmware source must satisfy both firmware columns; a task that edits the
host app must satisfy the host column.

| Property | Firmware — native (tree 1) | Firmware — source-scan (tree 2) | Host app (tree 3) |
|---|---|---|---|
| **Framework** | PlatformIO 6.2.0 + Unity, `platform = native`, ArduinoFake 0.4.0 | pytest 9.1.1, stdlib-only, **no `conftest.py`** (house rule), Python 3.12.14 | pytest + syrupy snapshots, `conftest.py`, `addopts = -ra -q`, **Python 3.11.16** |
| **Config file** | `firestarter_fw/platformio.ini` — `[native_base]` holds the single `test_filter` and `-I` list (20 entries each) | none | `firestarter_app/pyproject.toml` |
| **Runner path** | `pio` on `PATH` | **`/usr/local/py-utils/bin/pytest`** (a bare `python3 -m pytest` fails) | **`/workspaces/firestarter_app/.venv311/bin/python -m pytest`** |
| **Quick run command** | `pio test -e native -f "*<touched suite>*"` | `/usr/local/py-utils/bin/pytest tests/<module> -o addopts="" -p no:cacheprovider -q` | `.venv311/bin/python -m pytest tests/<module> -o addopts="" -p no:cacheprovider -q` |
| **Full suite command** | `pio test -e native` **and** `pio test -e native_nodevtools` | `/usr/local/py-utils/bin/pytest tests/ -v` | `.venv311/bin/python -m pytest tests/ -o addopts="" -q` |
| **Measured full runtime** | **31.3 s** (`native`) / **40.3 s** (`native_nodevtools`) | **11.6 s** (320 collected) | **180.6 s** (3 m 01 s) |
| **Measured per-suite runtime** | 0.6 s – 4.7 s (median ~2.0 s) | ~0.1 s – 1 s per module | ~1 s – 20 s per module |

### Measured baselines — unmodified trees, 2026-09-22

| Leg | Result | Note |
|---|---|---|
| `pio test -e native` | **20 suites, 243 cases, 243 succeeded, 31.3 s, exit 0** | green |
| `pio test -e native_nodevtools` | **243 cases, 243 succeeded, 40.3 s, exit 0** | green |
| `pytest tests/` (firmware) | **17 failed, 303 passed, 11.6 s** | ⚠️ **17 PRE-EXISTING RED**, all `test_flash_path_record_sync.py`. **Not caused by this phase.** Repaired by the first firmware task — see Wave 0. |
| `pytest tests/ --ignore=tests/test_flash_path_record_sync.py` | **279 passed, 10.7 s, exit 0** | the usable green baseline for tree 2 until the repair lands |
| host `pytest tests/` on 3.11 | **2309 passed, 0 failed, 36 snapshots passed, 180.6 s, exit 0** | green **with `/dev/ttyACM0` attached** — the recorded `test_no_programmer_found_*` trap did **not** fire |
| `pio run -e uno -e uno328pb -e leonardo` | 3 succeeded | figures in `205-RESEARCH.md` § Flash and RAM |

**Firmware phase gate** — `build.yml`'s four steps, in order: `pio test -e native` (**pull requests
only** — a branch push skips it), `pio test -e native_nodevtools` (always), `pytest tests/ -v`,
`pio run`.

**Host phase gate** — `ci.yml`'s four steps: `ruff check firestarter/ tests/`,
`ruff format --check firestarter/ tests/`,
`pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70`, and a
`pip install -e .` + `firestarter --help` smoke test. **`mypy` is not a host CI gate** — it runs only
in pre-commit — but `firestarter.cli_handlers` is in the strict island, so D-01's new code must be
fully annotated or pre-commit blocks the commit. `ruff`'s selection is `E,F,I,UP` with `E501`
ignored; a `# noqa` outside that set is inert.

---

## Sampling Rate

- **After every task commit:**
  - firmware-touching task → `/usr/local/py-utils/bin/pytest tests/ -o addopts="" -p no:cacheprovider -q`
    (**~11 s**; add `--ignore=tests/test_flash_path_record_sync.py` only until the Wave 0 repair
    lands) plus `pio test -e native -f "*<touched suite>*"` (**~2 s**)
  - host-touching task → `.venv311/bin/python -m pytest tests/<touched modules> -o addopts="" -q`
    (**~1–20 s**)
- **After every plan wave:** all four firmware `build.yml` legs in order (**~85 s**), plus the full
  host suite on 3.11 (**~181 s**), plus `ruff check` and `ruff format --check`.
- **Before `/gsd-verify-work`:** all four firmware legs green, host suite green on 3.11, the
  FWBLANK-05 table filled from a clean `pio run`, and the bench matrix recorded.
- **Max feedback latency:** **~11 s** (firmware source-scan) / **~2 s** (a filtered native suite).
  The only legs above 60 s are the full native runs and the host suite, both run at wave boundaries.

---

## Per-Task Verification Map

*Filled by the planner once task IDs exist. The requirement → command mapping below is the seed the
planner allocates across tasks; every row's command is measured-runnable today.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-T1 | 205-01 | 1 | FWBLANK-02 (host half), D-01/D-02/D-03 | T-205-01, T-205-03 | `erase -b` exits 0/1/2; a transport failure never reads as a chip verdict | unit + snapshot (host) | `cd /workspaces/firestarter_app && .venv311/bin/python -m pytest tests/test_cli_handlers.py -k erase -o addopts="" -p no:cacheprovider -v` | ❌ new legs — **W0**, seen RED first | ⬜ pending |
| 01-T2 | 205-01 | 1 | FWBLANK-02, OQ-1 | T-205-02, T-205-04 | `erase -s … -b` refused pre-wire, exit 2, one line, erase does not run | unit + snapshot (host) | `cd /workspaces/firestarter_app && .venv311/bin/python -m pytest tests/test_cli_handlers.py -k "erase and sector" -o addopts="" -p no:cacheprovider -v` | ❌ new legs — **W0**, seen RED first | ⬜ pending |
| 02-T1 | 205-02 | 1 | FWBLANK-05 (precondition), OQ-5 | T-205-06 | N/A | source-scan (fw tree 2) | `cd /workspaces/firestarter_fw && /usr/local/py-utils/bin/pytest tests/ -o addopts="" -p no:cacheprovider -q` | ✅ module exists, 4 literals repaired | ⬜ pending |
| 02-T2 | 205-02 | 1 | FWBLANK-05, D-10 | T-205-07, T-205-08 | N/A | build measurement | `cd /workspaces/firestarter_fw && pio run -t clean -e uno && pio run -t clean -e uno328pb && pio run -t clean -e leonardo && pio run -e uno -e uno328pb -e leonardo 2>&1 \| grep -E "^Processing\|^RAM:\|^Flash:"` | ❌ produces `205-FLASH-RAM.md` | ⬜ pending |
| 03-T1 | 205-03 | 2 | FWBLANK-01, FWBLANK-02, D-09, OQ-2 | T-205-09, T-205-11, T-205-13, T-205-14 | the write-init and erase-end pre-flights are gone and the host already owns both | source-scan + native + build | `cd /workspaces/firestarter_fw && /usr/local/py-utils/bin/pytest tests/test_verify_survival_source_contract.py tests/test_protocol_branch_inventory.py -o addopts="" -p no:cacheprovider -v` · `pio test -e native -f "*test_val_eprom*" -v` | ❌ new absence legs — **W0**, seen RED first | ⬜ pending |
| 03-T2 | 205-03 | 2 | FWBLANK-03, OQ-4 | T-205-12, T-205-14 | the sweep did not take `mem_util_operation_end`, the `region-end` clamp, or any in-algorithm verify | source-scan + native + build | `cd /workspaces/firestarter_fw && git grep -n -e "mem_util_blank_check" -e "blank_check_saved_address" -e "BLANK_CHECK_CHUNK_SIZE" -e "uint32_to_bytes" -- . ':!tests/test_verify_survival_source_contract.py'; echo "grep-exit:$?"` · `pio test -e native` | ❌ migrated survivor fence + new absence leg — **W0** | ⬜ pending |
| 04-T1 | 205-04 | 3 | FWBLANK-04, D-04, D-05 | T-205-15, T-205-17 | the retired bit exists nowhere and its gap carries a never-reuse record | source-scan + native + build | `cd /workspaces/firestarter_fw && git grep -n "FLAG_SKIP_BLANK_CHECK" -- src/ include/ test/ CLAUDE.md PROTOCOLS.md ':!tests/test_verify_survival_source_contract.py'; echo "grep-exit:$?"` · `pio test -e native_nodevtools` | ❌ new absence leg — **W0**, seen RED first | ⬜ pending |
| 04-T2 | 205-04 | 3 | FWBLANK-04, D-04 | T-205-15, T-205-19 | `-b` still reaches the Phase 203 guard without a wire bit | unit (host) | `cd /workspaces/firestarter_app && .venv311/bin/python -m pytest tests/test_write_blank_guard.py tests/test_write_blank_guard_pinning.py tests/test_chip_test_uv_slot_write.py tests/test_cli_handlers.py tests/test_eprom_operations.py -o addopts="" -p no:cacheprovider -v` | ✅ 14 legs re-anchor; 1 new ladder leg | ⬜ pending |
| 04-T3 | 205-04 | 3 | FWBLANK-04 | T-205-18 | a frozen report-group key is re-keyed as its own reviewable unit | unit (host) | `cd /workspaces/firestarter_app && .venv311/bin/python -m pytest tests/test_blast_radius_invariance.py -o addopts="" -p no:cacheprovider -v` | ✅ 3 legs re-key | ⬜ pending |
| 05-T1 | 205-05 | 4 | FWBLANK-01 (folded todo), OQ-3 | T-205-05, T-205-20 | a negative wire address is refused instead of clamping to 0, address field only | unit (native), BOTH envs | `cd /workspaces/firestarter_fw && pio test -e native -f "*test_read_timing*" -v` · `pio test -e native_nodevtools -f "*test_read_timing*" -v` | ❌ new cases in an existing suite — **W0**, seen RED first | ⬜ pending |
| 05-T2 | 205-05 | 4 | FWBLANK-01, FWBLANK-05 | T-205-21 | N/A | build measurement | `cd /workspaces/firestarter_fw && pio run -e uno -e uno328pb -e leonardo 2>&1 \| grep -E "^Processing\|^RAM:\|^Flash:"` | ✅ appends to `205-FLASH-RAM.md` | ⬜ pending |
| 06-T1 | 205-06 | 5 | FWBLANK-05, D-10 (edge E5 boundary, E6 precision) | T-205-22 | N/A | build measurement | `cd /workspaces/firestarter_fw && pio run -e uno -e uno328pb -e leonardo 2>&1 \| grep -E "^Processing\|^RAM:\|^Flash:"` | ✅ completes `205-FLASH-RAM.md` | ⬜ pending |
| 06-T2 | 205-06 | 5 | FWBLANK-05, D-08 | T-205-23, T-205-24, T-205-25 | a retired emit site does not free its id, and the host still renders 0xB0 for older firmware | codegen diff (meta) | `cd /workspaces && python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` + two `diff -u` regenerations | ✅ 204's executed shape (`694acce3`) | ⬜ pending |
| 07-T1 | 205-07 | 6 | D-06 (rig gate) | T-205-28, T-205-31 | no destructive leg runs before the operator names the part and the shield revision | **blocking human checkpoint** | none — `checkpoint:human-verify` | n/a | ⬜ pending |
| 07-T2 | 205-07 | 6 | FWBLANK-04, D-07 (criterion 3 setup + skew) | T-205-27, T-205-28, T-205-29, T-205-30 | pre-205 firmware refuses `write -b` from a post-205 host, captured verbatim | **bench** | `python3 -c "import glob,os; hits=[d for d in glob.glob('/sys/bus/usb/devices/*/') if os.path.exists(d+'idVendor') and open(d+'idVendor').read().strip()=='2341' and open(d+'idProduct').read().strip()=='8036']; assert len(hits)==1; assert os.path.exists('/dev/ttyACM0'); print('rig confirmed:', hits[0])"` · `pio run -e leonardo -t upload` | ❌ produces `205-BENCH-MATRIX.md` | ⬜ pending |
| 07-T3 | 205-07 | 6 | FWBLANK-01, FWBLANK-02 (criteria 3 and 5), D-01/D-06 | T-205-26, T-205-28 | a non-blank UV-handler part accepts a write unrefused; one part in two roles shows no other change | **bench** (erasable proxy for UV) | `cd /workspaces/firestarter_fw && pio run -e leonardo -t upload` · digest compares · `timeout 300 .venv311/bin/firestarter …` | ❌ produces `205-BENCH-MATRIX.md`, `205-SESSION-COST.md` | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] **Repair `tests/test_flash_path_record_sync.py`** (`:77`, `:363`, `:1092`, `:1094`) so tree 2
      has a reachable green — four string literals, `.planning/` → `.planning/milestones/`.
      **Owner: first firmware task.** Without this, every firmware `<fails_when>` that says "the tree
      is green" is false at the start.
- [ ] **Migrate the `mem_util_operation_end` survivor leg** out of
      `tests/test_blank_check_region_source_contract.py` before retiring that module — plus
      `test_scan_targets_are_non_vacuous` and `test_this_module_cannot_be_silently_skipped`, which
      give it its anti-vacuity guarantees. Destination:
      `tests/test_verify_survival_source_contract.py`. **Same commit as the deletion.**
- [ ] **FWBLANK-01/02/03/04 absence legs** in `tests/test_verify_survival_source_contract.py` — each
      **seen RED against the pre-sweep tree** before the sweep lands.
- [ ] **Host legs for D-01/D-02/D-03** in `tests/test_cli_handlers.py`: the 0/1/2 exit mapping, the
      terse single-line refusal, the absence of `--full` on `erase`, and the OQ-1 `-s` + `-b`
      refusal.
- [ ] **`tests/fake_chip.py` re-key** (`:34`, `:315`): it models a firmware pre-flight that will not
      exist. Decide whether it models pre-205 firmware (keep, rename to say so) or is retired.
      `:318`/`:340`'s `MSG_ERR_NOT_BLANK` assignments stay correct either way.
- [ ] **Native suite re-keys — 12 lines in 8 files** (enumerated in `205-RESEARCH.md` § Gate Impact),
      split so every commit boundary is green.
- [ ] **Gate re-anchors:** `test_config_schema_pinned.py` `_C14_CONSUMER_SITES` 102→101, 108→107;
      `test_protocol_branch_inventory.py` `[67]`→`[64]`; the golden re-derive and
      `meta.blob_shas["src/proms/eprom.cpp"]` — **all three in the ONE commit that carries the
      `eprom.cpp`/`firestarter.cpp` edits**.
- [ ] **The frozen-hash re-key in `test_blast_radius_invariance.py` as its own commit**, per the
      gate's own instruction.
- [ ] **Negative-address native cases** in `test/native/avr/test_read_timing/`, run under both native
      envs.
- [ ] No new PlatformIO suite directory is needed — the folded fix reuses `test_read_timing`, so
      `[native_base]`'s `test_filter` and `-I` lists do **not** change.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|---|---|---|---|
| A write to a non-blank UV part reaches the firmware unrefused and programs the region it was given | criterion 3 | the outcome is a property of silicon; `firestarter.cpp` and `eprom_operations.cpp` are outside `build_src_filter`, so no native test links the dispatch path | bench B5, per `205-RESEARCH.md` § Bench |
| No behaviour change across one UV part and one erasable part other than where the refusal comes from | criterion 5 | same | bench B6 |
| The D-04 skew: pre-205 firmware refuses `write -b` from a post-205 host | D-04 / D-07 | needs two real firmware artifacts on real hardware | bench B3, **before** reflashing |
| `erase -b` added wall-clock | D-01 / Phase 206 SESS-01 | a real port open on a real board | bench B7, or `tests/test_connect_cost_harness.py` if a derivation is accepted |
| Flash/RAM reclaim | FWBLANK-05 | `scripts/baseline/check_size_baseline.py` does not exist; no CI leg gates image size | `pio run` before and after, by hand |

**Bench rig, verified 2026-09-22:** `/dev/ttyACM0` = `usb-Arduino_LLC_Arduino_Leonardo-if00`, the
only serial device present. The Uno-class gap is physically real and does not block any criterion.
**Parts:** operator seats a **W27C512** (erasable). No true UV part is available this phase — the
erasable part rides the UV handler as the **firmware proxy** for the UV legs, as this project has
done before. Every bench leg that stands in for UV silicon must record that it ran on a proxy.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies — 14 of 15 tasks carry runnable automated commands; task 07-T1 is a `checkpoint:human-verify` by design and gates destructive hardware work rather than asserting a property.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify — the longest run without one is a single task (07-T1).
- [x] Wave 0 covers all MISSING references — every ❌ row above names the plan and task that creates the missing leg, and each new absence leg carries a seen-RED-first instruction with its transcript required in the plan's SUMMARY.
- [x] No watch-mode flags — every command is a single-shot run; `pio test`, `pio run` and `pytest` are all invoked without watchers, and `-o addopts=""` is used so the doubled `-q` cannot hide a count line.
- [x] Feedback latency < 15s — the per-task loop is the firmware source-scan tree at ~11 s or a filtered native suite at ~2 s; the only legs above 60 s are the full native runs and the host suite, both at wave boundaries.
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** per-task map filled by plan-phase on 2026-09-22; 15 tasks across 7 plans, every task carrying an automated verify or a stated Wave 0 dependency, and the one task without an automated command is a blocking human checkpoint by design.
