---
phase: 144
slug: tests-build-verification
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-13
---

# Phase 144 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `144-RESEARCH.md` § Validation Architecture. This phase is **dual-repo** (D-19), so
> every row names which repo it runs in.
>
> **The inverted question.** This phase's deliverables are *gates*. A gate that passes proves nothing
> until it has been seen to fail for the right reason **and** pass for the right reason. D-18 states
> the first half; the unreachable-leg trap states the second. Both transcripts are required evidence.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (firmware gates)** | `pytest` — `firestarter/tests/`, stdlib + pytest only, **no `conftest.py` anywhere in the repo** (house rule) |
| **Framework (firmware native)** | Unity + ArduinoFake via PlatformIO (`test_framework = unity`) |
| **Framework (host gates)** | `pytest` on `.venv/ci-replica/bin/python` (3.11.15) — CI parity, never ambient 3.12 (D-21) |
| **Config file (firmware)** | none for pytest; `firestarter/platformio.ini` for the six native envs |
| **Config file (host)** | `firestarter_app/pyproject.toml` — `addopts = "-ra -q"` :107, `# mypy_error_watermark = 35` :174, ruff `py39`/88 :110-111 |
| **Quick run (firmware)** | `cd /workspaces/firestarter && python3 -m pytest tests/ -q` → **292 passed**, ~14 s |
| **Quick run (host, one module)** | `cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/<module> -o addopts="" -q` → ~0.1–0.2 s |
| **Full suite (firmware native, pinned)** | `pio test -e native` and `pio test -e native_nodevtools` — 141 cases / 17 suites each |
| **Full suite (firmware native, v131)** | `pio test -e native_params_v131` (9), `-e native_loop_v131` (79 = 47+32, two suites), `-e native_trace_v131` (5, **3 RED by design** until D-06/D-08 land) |
| **Full suite (host)** | `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" --cov=firestarter --cov-report=term-missing --cov-fail-under=70` → baseline **1578 passed, 82.92%**, ~230 s |
| **Estimated runtime** | ~14 s firmware pytest · sub-second host module · ~230 s host full · ~4 min three AVR builds cold |

`-o addopts=""` is **required** on every host run — `addopts` already carries `-q` and doubling it
suppresses the count line the record needs.

---

## Sampling Rate

- **After every task commit (firmware):** `python3 -m pytest tests/ -q` (292, ~14 s). **Commit
  first** — `test_flash_path_record_sync.py` asserts the whole firmware repo's `git status
  --porcelain` (F-09 / D-20), so any untracked file turns it RED.
- **After every task commit (host):** the touched module on the replica —
  `.venv/ci-replica/bin/python -m pytest tests/<module> -o addopts="" -q`. The **firmware** repo must
  already be clean: `test_py32_flash_map_host.py` asserts `_git_porcelain(FW_ROOT) == ""` for the
  *sibling* repo, so a firmware work-in-progress turns the **host** suite RED (F-09 / Pitfall 7).
- **After every plan wave (firmware):** firmware pytest (292) + both pinned native envs (141 cases /
  17 suites each) + all three `*_v131` envs **by name** + `python3 scripts/check_build_warnings.py`.
- **After every plan wave (host):** F-12's four CI-scoped commands (`ci.yml` :81 / :84 / :87 / :90 —
  **C-02**, not ":80–:87") + the full replica suite with coverage.
- **Phase gate:** the whole of F-12's command set, **cold**, every verdict captured verbatim. This is
  D-02's "ONE cold consolidated run" — no citing of the owning phases' recorded runs.
- **Max feedback latency:** 15 s (firmware pytest) / sub-second (host module).

---

## Per-Task Verification Map

Task IDs are assigned by the planner. Until plans exist, the contract is requirement-level; each plan
MUST refine these rows into `144-{plan}-{task}` IDs and carry the command in its
`<verify><automated>` block. **Plan column `TBD` is a Wave-0 debt, not an exemption.**

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | 1 | TEST-01 | — | N/A | unit (Unity) | `pio test -e native_params_v131` (9 cases) | ✅ | ⬜ pending |
| TBD | TBD | 1 | TEST-01…05 | V5 / V14 | Empty or misdirected parse **fails closed** (non-vacuity floor ≥ 88 extracted names) | gate (pytest, static source scan) | `python3 -m pytest tests/test_requirement_case_mapping_v131.py -q` (firmware) | ❌ W0 (D-01) | ⬜ pending |
| TBD | TBD | 1 | TEST-01…05 | V14 | Seam overrides a **path only**, never a marker name or policy literal; one leg recomputes the default root without reading `os.environ` | gate (pytest, non-vacuity half) | same module | ❌ W0 (D-01) | ⬜ pending |
| TBD | TBD | 1 | TEST-02 | — | N/A — fixed-width pulse, no escalation between attempts | unit (Unity) | `pio test -e native_loop_v131 -f "*test_loop_eprom_v131*"` (4 `test_loop01_*`) | ✅ within 47 | ⬜ pending |
| TBD | TBD | 1 | TEST-03 | — | Arithmetic proven; **in-loop wiring on a live row is an explicit NON-CLAIM** (D-03) | unit (Unity) | same — 5 `test_loop03_*` + `test_loop04_no_live_row_emits_an_overprogram_pulse` | ✅ within 47 | ⬜ pending |
| TBD | TBD | 1 | TEST-04 | — | Max-pulse failure aborts the block, reports the address, disables every HV route **in the emitted register stream only** — never on a part | unit (Unity) | `pio test -e native_loop_v131` (both suites) — 3 `test_loop05_*` + `test_vpp02_{x3,x4,e1}` | ✅ 47 + 32 | ⬜ pending |
| TBD | TBD | 1 | TEST-05 | — | N/A — `0xFF`/already-matching skips + `pulse_delay == 0` fallback | unit (Unity) | `pio test -e native_loop_v131` + `-e native_params_v131` — 4 `test_loop06_*` + **six** params fallback cases (**C-04**: CONTEXT.md's "two fallback cases" names no existing pair) | ✅ | ⬜ pending |
| TBD | TBD | 2 | TEST-06 | V12 | Rename preserves the artifact: `ca3e09f164e6e1c541ecb63d15bbebf5bce41d70` still resolves after `git mv` | gate (pytest, blob identity) | `git rev-parse HEAD:firestarter/test/native/avr/_shared/eprom_v131_expected_prechange.h` | ✅ manual-only (D-08 leaves it un-gated **by choice**) | ⬜ pending |
| TBD | TBD | 2 | TEST-06 | — | Fresh capture at **this phase's tip**, never a paste of `141-NEW-TRACE.md`'s stale 91/119/59 | integration (Unity) | `pio test -e native_trace_v131` → 5 cases, 0 failed. Expected totals **91 / 115 / 59** — deviation is stop-and-report | ✅ suite exists, 3 RED by design | ⬜ pending |
| TBD | TBD | 2 | TEST-06 | V5 | Six-assertion identity gate re-armed on the **new** fixture; goldens re-derived by independent parse, never hand-edited | gate (pytest) | `python3 -m pytest tests/test_golden_trace_identity_eprom_v131.py -q` | ✅ module exists (currently GREEN on the OLD fixture) | ⬜ pending |
| TBD | TBD | 2 | TEST-06 | V5 / V12 | **All 885 entries** (620 old + 265 new) fall in exactly one attributed segment; an unattributed entry is **locatable**, not just counted | gate (pytest, static, state machine) | `python3 -m pytest tests/test_trace_segment_exhaustiveness_v131.py -q` | ❌ W0 (D-07) | ⬜ pending |
| TBD | TBD | 3 | TEST-07 | — | N/A | gate | `python3 -m pytest tests/ -q` (firmware) → 292 | ✅ | ⬜ pending |
| TBD | TBD | 3 | TEST-07 | — | Cold measurement, not warm-cache (Pitfall 6) | build | `pio run -t clean -e <env>` **then** `pio run -e <env>` for `uno`, `uno328pb`, `leonardo` | ✅ | ⬜ pending |
| TBD | TBD | 3 | TEST-07 | — | Pinned envs may never absorb a new suite | gate | `pio test -e native` + `pio test -e native_nodevtools` → 141 / 17 each | ✅ | ⬜ pending |
| TBD | TBD | 3 | TEST-07 | — | Parity proven in the **present** direction, verbatim | gate (pytest) | `.venv/ci-replica/bin/python -m pytest tests/test_revision_constants_parity.py -o addopts="" -q` → **14 passed** (verified in research) | ✅ | ⬜ pending |
| TBD | TBD | 3 | TEST-07 | V14 | Absent path **skips cleanly** rather than erroring — MUST be a **child process**; `monkeypatch.setenv` cannot work (import-time + collection-time binding, C-15) | gate (pytest, subprocess) | `FIRESTARTER_FW_ROOT=<empty dir> … -rs -q` → **6 passed, 8 skipped** (verified in research) | ✅ | ⬜ pending |
| TBD | TBD | 3 | TEST-07 | V5 / V12 | CAP-03 pack order asserted at the **computed `ver_end`**, never a fixed index; silent capability loss caught loudly | gate (pytest, cross-repo static) | `.venv/ci-replica/bin/python -m pytest tests/test_cap03_ack_layout_parity.py -o addopts="" -q` | ❌ W0 (D-17) | ⬜ pending |
| TBD | TBD | 3 | TEST-07 | — | CI-scoped, not devcontainer-scoped (3.11 replica) | gate | F-12's four commands verbatim — `ci.yml` :81 / :84 / :87 / :90 (**C-02**) | ✅ | ⬜ pending |
| TBD | TBD | 4 | TEST-08 | — | Measured against the **PREP-03 anchor** (`size_baseline.json`, 23954/24004/26016 — D-09) | gate | `python3 scripts/check_size_baseline.py --avr-log uno=… --avr-log uno328pb=… --avr-log leonardo=…` (default baseline) | ✅ | ⬜ pending |
| TBD | TBD | 4 | TEST-08 | Repudiation | **Green is disclosed as "the anchor moved to v1.31", never "growth stayed inside the band"** (D-14, Pitfall 4) | gate | `… --policy merge05 --baseline scripts/baseline/size_baseline_base01.json` | ✅ | ⬜ pending |
| TBD | TBD | 4 | TEST-08 | — | Leonardo ceiling checked **explicitly**, not discovered — 93.8%, 1766 B headroom | gate | same, plus the recorded per-target table | ✅ | ⬜ pending |
| TBD | TBD | 4 | TEST-08 | — | Watermarks unchanged and unforgiving: native `<= 1166` **zero headroom**, AVR `== 0` (D-23) | gate | `python3 scripts/check_build_warnings.py` per env — **never** with a `*_v131` env name (D-22, refined by **C-03**) | ✅ | ⬜ pending |
| TBD | TBD | 4 | TEST-08 | — | `size_baseline_v131.json` refresh must **ADD two env records**, not update three (**C-01**) | record | re-derived from the same consolidated run; no live gate reads this file | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter/tests/test_requirement_case_mapping_v131.py` — TEST-01…05 (D-01). **A pytest
      module, NOT a `scripts/check_*.py`** — `test_checker_convention.py`'s `FLOOR = 6` and
      `FIXTURE_FLOOR = 15` sit at *exactly* the current counts, so a `scripts/` checker obliges five
      coordinated same-commit edits including raising both floors (F-08).
- [ ] `firestarter/tests/test_trace_segment_exhaustiveness_v131.py` — TEST-06 (D-07). Segmentation is
      a **state machine**, not a field lookup: `pin_CE` (38 per array) spans both the pulse and
      verify-read segments; the `OUTPUT_ENABLE` toggle is the discriminator (F-07).
- [ ] `firestarter_app/tests/test_cap03_ack_layout_parity.py` — TEST-07 (D-17), behind
      `requires_fw` / `fw_path`.
- [ ] `firestarter_app/tests/fixtures/planted_cap03_*.cpp` — D-18's two committed planted violations
      for the above (the `FIRMWARE_HEADER` pattern at `test_revision_constants_parity.py:148` / `:733`).
- [ ] Planted-violation inputs for the two firmware gates — scratch copies reached via the
      import-time env seam; prefer a **committed** fixture where the input is small (F-15).
- [ ] `firestarter/test/native/avr/_shared/eprom_v131_expected_prechange.h` — D-05's pure rename.
      **D-05 + D-06 + D-08 must land in ONE commit** (F-05): the identity gate reads `HEAD:`, not the
      worktree, so a bare `git mv` fails *inside git's exit-code assert* rather than reporting a SHA
      mismatch. Predict the new SHA with `git hash-object` before staging.
- [ ] `firestarter/tests/golden/eprom_v131_trace_inventory.json` — re-pointed at the new fixture only;
      `meta.how_to_update` is binding (independent parse, never a hand-edited count).
- [ ] Framework install: **none required.** Both suites already run.

**D-18 obligation:** every new gate leg above must be **seen RED on a planted violation** *and* **seen
GREEN for the right reason**, both transcripts verbatim in the owning plan's SUMMARY. A pre-authored
leg can be unreachable — RED alone proves nothing (Pitfall 3).

**D-04 invariant:** **no file under `firestarter/src/` may be edited this phase.** A plan that finds
itself needing one must **stop and report**, not absorb it. Both `protocol_branch_inventory.json` pins
(`cedc88dc…` / `5dffe841…`) match `HEAD` right now, so the golden stays green throughout — a first for
this milestone.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `eprom_v131_expected_prechange.h` is the preserved Phase-138 artifact | TEST-06 | D-08 leaves the pre-change file **deliberately un-gated** — one inventory record, one target | `git rev-parse HEAD:firestarter/test/native/avr/_shared/eprom_v131_expected_prechange.h` must print `ca3e09f164e6e1c541ecb63d15bbebf5bce41d70`. Record as a **named gap**, do not imply machine coverage |
| The three `*_v131` envs actually ran | TEST-07 | D-15: they are wired into **no CI leg**. A local run-by-name obligation, recorded loudly | Run each by name and paste the verdict. **Never imply CI covers these envs** |
| Any claim about real silicon | TEST-01…08 | Out of scope — bench evidence is **Phase 145** | Do not claim it here. TEST-04's "disables every high-voltage route" is proven in the emitted control-register stream only |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15 s
- [ ] Every `<automated>` block contains real shell bytes — **no HTML entities** (`&amp;&amp;` for
      `&&` made 30/37 legs unrunnable in a prior phase; check the bytes on disk, not the rendered view)
- [ ] Every planted-violation write goes under `tmp_path` (or a committed `tests/fixtures/` path) and
      asserts the **real** file's blob SHA is unchanged before and after (V12 ceremony,
      `test_flash_path_record_sync.py:1242-1250`)
- [ ] No `subprocess` call uses `shell=True`; list-form argv only
- [ ] Every new module carries a non-vacuity floor as a **hardcoded literal**, and a self-check that
      the module contains no `pytest.skip` / `@pytest.mark.skipif`
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
