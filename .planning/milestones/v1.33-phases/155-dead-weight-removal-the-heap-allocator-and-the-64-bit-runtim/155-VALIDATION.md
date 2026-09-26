---
phase: 155
slug: dead-weight-removal-the-heap-allocator-and-the-64-bit-runtime-firmware-only
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-08-23
signed_off: 2026-08-23
---

# Phase 155 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `155-RESEARCH.md` §Validation Architecture, where every figure below was measured
> at `firestarter` `2ad5b32` on a clean tree — not carried from ROADMAP.md.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | **Unity** (native, PlatformIO `test_framework = unity`) + **pytest** (host-side script/source gates) |
| **Config file** | `firestarter/platformio.ini` |
| **Quick run command** | `pio test -e native` (~24 s) |
| **Full suite command** | `pio test -e native && pio test -e native_nodevtools && python3 -m pytest tests/ -q` |
| **Estimated runtime** | ~73 s (23.9 + 37.1 + 11.9) |
| **CI legs (exactly three)** | `pio test -e native` (`build.yml:142`) · `pio test -e native_nodevtools` (`:155`) · `pytest tests/ -v` (`:161`) |
| **Non-CI local gates** | `scripts/check_size_baseline.py`, `scripts/check_build_warnings.py` — invoked by **no** workflow |

**Measured baseline at `2ad5b32`, clean tree:**

| Leg | Result |
|-----|--------|
| `pio test -e native` | **172 cases / 172 succeeded**, 17 suites, 23.9 s |
| `pio test -e native_nodevtools` | **172 cases / 172 succeeded**, 17 suites, 37.1 s |
| `python3 -m pytest tests/` | **323 passed**, 11.9 s |
| `pio run -e uno` | flash **26026**, RAM **1575** |
| `pio run -e uno328pb` | flash **26074**, RAM **1581** |
| `pio run -e leonardo` | flash **28170**, RAM **2016** |

---

## Sampling Rate

- **After every task commit:** `pio test -e native` (23.9 s) — catches the DEAD-06 build break immediately.
- **After every plan wave:** `pio test -e native && pio test -e native_nodevtools && python3 -m pytest tests/ -q`
  — **run only after the firmware commit lands**; `tests/test_flash_path_record_sync.py` asserts whole-repo porcelain.
- **Before `/gsd-verify-work`:** all eight phase-gate legs green (below).
- **Max feedback latency:** 24 s (quick) / 73 s (full).

**Phase gate — all eight must be green:**

1. `pio test -e native` → **172/172, 17 suites** (the count is an exact `compare_native` input — it must stay 172)
2. `pio test -e native_nodevtools` → **172/172, 17 suites**
3. `python3 -m pytest tests/ -q` → **≥323 passed**, 0 failed — after the firmware commit lands
4. `avr-nm` heap gate → `0` on all three ELFs
5. `avr-nm` 64-bit gate (**11 symbols**, not 8) → `0` on all three ELFs
6. `pio run -e {uno,uno328pb,leonardo}` → flash/RAM recorded, delta vs the **pre-change same-tree** figures above
7. `scripts/check_size_baseline.py` → green, recorded as one-sided, and **NOT re-anchored** (LAND-01 / Phase 158 owns that)
8. `scripts/check_build_warnings.py` → no new warning on `memory.cpp`, `rurp_common.cpp`, `firestarter.h`

---

## Per-Task Verification Map

*Task IDs are assigned by the planner; this map is completed at plan time. The requirement→check
mapping below is fixed by research and is what each task must inherit.*

| Task ID | Plan | Wave | Requirement | Behaviour to prove | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|--------------------|-----------|-------------------|-------------|--------|
| TBD | TBD | **0** | DEAD-01, DEAD-03 | pre-change before-figures captured (symbol table, sole-caller attribution, 3 flash/RAM pairs, `rurp_read_voltage_mv`=434 B, `mem_util_blank_check`=510 B, `handle`=603/603/1115 B) | measurement | `avr-nm --print-size --size-sort -C` + `avr-objdump -d` + `pio run -e {uno,uno328pb,leonardo}` | ❌ **W0** | ⬜ pending |
| TBD | TBD | **0** | DEAD-01, DEAD-03 | heap + 64-bit symbol gate exists and is fail-closed | script gate | `python3 scripts/check_no_heap_or_64bit_symbols.py` (name illustrative) | ❌ **W0** | ⬜ pending |
| TBD | TBD | **0** | DEAD-01, DEAD-03 | that gate is **not hollow** — a planted `malloc` turns it RED | planted negative | reinstate one `malloc` in a throwaway worktree, run the gate, record RED | ❌ **W0** | ⬜ pending |
| TBD | TBD | **0** | DEAD-04, DEAD-05 | numerical oracle + source-contract scan | pytest | `python3 -m pytest tests/test_voltage_reformulation_oracle.py -q` | ❌ **W0** | ⬜ pending |
| TBD | TBD | 1+ | DEAD-01 | no `malloc`/`free`/`realloc`/`calloc`/`__brkval` in any of 3 images | image/link assertion | `avr-nm` gate → `heap=0` ×3 | ❌ W0 | ⬜ pending |
| TBD | TBD | 1+ | DEAD-02 | unchecked deref removed; recorded as a **latent defect closed** | source diff + phase record | `git diff` shows `memory.cpp:502-500` gone; subsumed by the DEAD-01 gate | ✅ | ⬜ pending |
| TBD | TBD | 1+ | DEAD-03 | no 64-bit runtime helper in any of 3 images | image/link assertion | `avr-nm` gate over **11** symbols → `64bit=0` ×3 | ❌ W0 | ⬜ pending |
| TBD | TBD | 1+ | DEAD-03 | `rurp_read_voltage_mv` body 434 → ~230 B; no `uint64_t` reappears | size + source contract | `avr-nm --print-size \| grep read_voltage_mv`; pytest `"uint64_t" not in fn` | ❌ W0 | ⬜ pending |
| TBD | TBD | 1+ | DEAD-04 | bit-identity at shipped calibration; ≤5 mV over the grid; **both guards**; `r2==0` → 0 | numerical oracle | same pytest file — grid (470,016 evals / 0.44 s) **+ 4 guard-boundary cases + 2 sentinels** | ❌ W0 | ⬜ pending |
| TBD | TBD | 1+ | DEAD-04 | the shipped C **is** the formula the oracle models | source contract | same pytest file, comment-stripped scan of `rurp_common.cpp` | ❌ W0 | ⬜ pending |
| TBD | TBD | 1+ | DEAD-05 | no phase artefact implies native or bench coverage | negative assertion over prose | grep phase artefacts for the forbidden phrasings (below) | ❌ W0 | ⬜ pending |
| TBD | TBD | 1+ | DEAD-06 | both suites updated; behaviour still pinned; alternative recorded with its cost | native regression | `pio test -e native` / `-e native_nodevtools` → **172/172, 17 suites** | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**DEAD-06 cannot go vacuous:** removing `progress_data` from the handle is **compiler-forced** — both suites
fail to *build* with `error: ... has no member named 'progress_data'` (executed in research; 172 → 127 cases).
The test edit must land in the **same commit** as the header edit.

---

## Wave 0 Requirements

- [ ] **Pre-change before-figures, captured and committed before any edit** — DEAD-01, DEAD-03.
      **Irrecoverable afterwards**, and Phases 156–158 each invalidate them.
- [ ] **`scripts/check_no_heap_or_64bit_symbols.py`** (or a shell gate) — DEAD-01, DEAD-03.
      Must be **fail-closed on a missing ELF** and must **not** rely on `grep`'s exit status.
- [ ] **A planted negative for that gate** — reinstate one `malloc` in a throwaway worktree, confirm RED, record it.
      Without this it is a hollow gate by this repo's own standard.
- [ ] **`tests/test_voltage_reformulation_oracle.py`** — DEAD-04, DEAD-05. Two halves: the numerical grid
      (grid + 4 guard-boundary cases + 2 sentinel cases) **and** the comment-stripped source-contract scan.
      Lands in **CI leg 3**. `_strip_comments` copied from `tests/test_write_path_source_contract_v131.py:223`.
- [ ] **Exact `(r1, r2)` pair straddling `k = 4194303`** — computed at plan time, not searched at runtime.
- [ ] **Nothing needed for DEAD-06** — both suites exist and the change is compiler-forced.
- [ ] **Framework install:** none. Use system `python3 -m pytest`, not the pio penv.

---

## ⚠ The Honest Coverage Ceiling — DEAD-04 and DEAD-05

**This must appear, in these terms, in every plan, every SUMMARY, and the phase record.**

`src/boards/rurp_common.cpp` is compiled by **no** native environment. All six native envs share
`build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>`
(`platformio.ini:227`, `:307`). Therefore:

1. **`rurp_read_voltage_mv` has ZERO native unit-test coverage, before and after this phase.** In native
   builds it is a stub (`test/native/avr/_shared/host_stubs_common.inc:275` returns 0; four suites override
   with `set_mock_vpp_mv`). Every native VPP test exercises the *consumer* against a mock, never this arithmetic.
2. **DEAD-04's oracle is a HOST-SIDE NUMERICAL MODEL, not a test of compiled firmware.** It proves two integer
   formulas agree over a stated grid, and — via the source-contract scan — that the shipped C is textually the
   formula modelled. It does **not** execute AVR code.
3. **There is NO bench coverage, and none will be created.** D-02 forbids it. Native trace stubs record no time
   (`delay()` unstubbed), so no trace diff could contribute even if the TU compiled.
4. **Residual risk, named:** avr-gcc miscompiling 32-bit `uint32_t` multiply/divide. **Unmitigated by any
   artefact of this phase.** Mitigated only by that being AVR's most-exercised path, and by the change
   *reducing* codegen complexity. Say this; do not imply it is covered.
5. **Forbidden phrasings** about this function in any Phase 155 artefact: *"tested"*, *"unit-tested"*,
   *"covered by native"*, *"verified on hardware"*, *"bench-verified"*, *"proven at runtime"*.
   **Correct phrasing:** *"proven by a committed host-side numerical oracle over a stated input grid, bound to
   the shipped C by a source-contract scan; no native and no bench coverage exists."*
6. ⚠ **The preserved reference (`a6b46f8`) gets this wrong.** Its `rurp_common.cpp` comment reads *"this
   arithmetic is **bench-verified only**"* — false, and a direct DEAD-05/D-02 violation. **Copying that comment
   across unedited is the single most likely way this phase fails DEAD-05.**

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | — | — |

**All phase behaviors have automated verification**, with two stated exceptions that are *documentation
obligations*, not manual tests:
- **DEAD-02** — the *record* of the latent defect closed is the deliverable; the code change itself is
  covered by the DEAD-01 symbol gate.
- **DEAD-05** — a requirement about the honesty of wording. Mechanised as a negative grep over this phase's
  own artefacts (see Wave 0), which is the strongest available check; it cannot prove prose is *complete*.

**No bench/hardware leg exists in this phase, by decision (D-02), and none may be implied.**

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (4 items above) — all four landed: before-figures (155-01), symbol gate (155-02), planted negative (155-02 + 155-06), oracle (155-04)
- [x] Planted negative recorded RED for the symbol gate — **both directions**: committed pre-change listing (155-02) and a post-change throwaway worktree (155-06). 155-06's first attempt was silently optimised away by the compiler and was corrected to a store/read-back shape that cannot be elided
- [x] Both `k`-guard boundary cases and both sentinel cases present in the oracle — the nominal grid reaches neither guard (`k` maxes at 8715 vs 4194303), so the four dedicated boundary pairs are what discharge the clause
- [x] No watch-mode flags
- [x] Feedback latency < 24 s (quick) / 73 s (full)
- [x] Native case count still **172 / 17 suites** on both native legs — measured, not assumed
- [x] `size_baseline.json` **not** re-anchored — byte-unchanged, confirmed by the verifier
- [x] No forbidden coverage phrasing in any Phase 155 artefact — gate exit 0 over the 22-file corpus, three named exclusions, SUMMARY class NOT exempted
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-08-23 — closed out by the execute-phase orchestrator after `155-VERIFICATION.md` returned `status: passed` (6/6 must-haves, independently re-measured). Per-task IDs in the map above were deliberately left as `TBD` rather than back-filled: the authoritative per-task evidence lives in `155-01-SUMMARY.md`…`155-06-SUMMARY.md` and in `.planning/v1.33/155-after-figures.md`, and inventing IDs here would add a second, driftable record of it.
