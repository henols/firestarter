---
phase: 157
slug: command-decode-table-handle-type-narrowing-firmware-only
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-23
---

# Phase 157 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `157-RESEARCH.md` §Validation Architecture, where every figure below was measured
> at `firestarter` `1151dc4` on a clean tree — the reference implementation was **built and run**
> this session on all three AVR targets plus both native envs, **not** carried from ROADMAP.md,
> **sixteen** of whose figures the research corrects (C-1 … C-16).

**Two operator decisions are load-bearing for everything below** (settled at plan time, the same
way Phase 156 settled OD-2):

- **OD-1 — out-of-range policy is saturate-for-ordinals, MASK-for-bitmasks, reject-for-nothing.**
  The reference patch saturated `ctrl_flags` to `0xFFFF`, which sets every control flag including
  `FLAG_FORCE`, `FLAG_SKIP_ERASE` and `FLAG_SKIP_BLANK_CHECK` — **fail-open, in the phase whose
  headline criterion is fail-closed** (F-1 / C-7). `ctrl_flags` masks. `reject` is declined
  because it needs a new message id → meta-repo `messages.toml` → codegen, which would break the
  firmware-only property; that alternative is recorded with its cost, not silently dropped.
- **OD-2 — the identifier `key_parsers` is KEPT.** Renaming it turns
  `firestarter_app/tests/test_json_key_parity.py::test_page_size_key_string_matches_constants_py`
  RED and makes its sibling leg pass **vacuously** (empty regex match = fail-open) — measured, 3
  failures against a 24-passed baseline (F-2). Keeping the name costs nothing, keeps the cross-repo
  gate honest, and keeps Phase 157 firmware-only with **zero** `firestarter_app` commits. The
  record must state that the identifier is now slightly stale — it becomes a data table of
  `{key, offset, width, clamp}`, not a table of parsers — and why it was kept.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | **Unity**, via PlatformIO `test_framework = unity` (`platformio.ini`), plus **ArduinoFake 0.4.0** for Arduino stubs |
| **Config file** | `firestarter/platformio.ini` — `[env:native]` and `[env:native_nodevtools]`, each with a **17-entry `test_filter`** and a matching 17-entry `-I` list that **must stay in lockstep** |
| **Production TUs in the native envs** | `build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>` — **`src/json_parser.c` is IN** (Phase 44 Plan 02), and `src/proms/memory.cpp` is in via `+<proms/>` |
| **Quick run command** | `pio test -e native -f "*test_read_timing*"` (the suite this phase extends) |
| **Full suite command** | `pio test -e native && pio test -e native_nodevtools` |
| **Host gate command** | `cd /workspaces/firestarter_app && python3 -m pytest tests/ -q -o addopts=""` — run **only on a committed firmware tree** |
| **Build gate** | `pio run -e uno && pio run -e uno328pb && pio run -e leonardo` — AVR warning policy is `== 0` |
| **Size gate** | `python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --rebuild` — **local-run only, in NO CI workflow** |
| **CI legs, exhaustively** | `pio test -e native` · `pio test -e native_nodevtools` · `pytest tests/` · `pio run`. **Nothing else.** `check_size_baseline.py` and `check_build_warnings.py` are local obligations. |

**Measured baseline at `1151dc4`, clean tree — executed this session:**

| Leg | Baseline |
|-----|----------|
| `pio test -e native` | **172 cases / 17 suites / 172 succeeded** (19.8 s) |
| `pio test -e native_nodevtools` | **172 / 17 / 172** (29.9 s) |
| `pytest tests/` (host) | **1976 passed / 0 failed / 0 skipped** (241 s), 32 syrupy snapshots |
| AVR warnings | 0 / 0 / 0 |
| `test_read_timing` cases | **9** (`RUN_TEST` at `:185-193`) |
| `pio run -e uno` | flash **24234**, RAM **1567** |
| `pio run -e uno328pb` | flash **24282**, RAM **1573** |
| `pio run -e leonardo` | flash **26378**, RAM **2008** |
| `size_baseline.json` `native.cases` | 172 |
| `size_baseline_base01.json` `native.cases` | **141** (frozen at Phase 124 — the pre-existing RED) |

**Target, measured on the built reference implementation (all three targets):** flash
`24234→23086` / `24282→23134` / `26378→25230` = **−1148 B** each; RAM `1567→1562` / `1573→1568` /
`2008→2003` = **−5 B** each.

**⚠ C-19 — those figures predate OD-1's mask policy and must NOT be chased.** The reference
implementation was measured on a table with **no policy column**. OD-1 adds one (mask-vs-saturate
per row), which costs bytes. A post-change figure that still reads **exactly** −1148 is therefore
the *suspicious* outcome, not the target. Record what the tree actually measures; do not tune the
implementation toward a number taken before the policy existed. The **−890 / −258** split (C-3,
superseding the ROADMAP's −976 / −172) carries the same caveat.

---

## Sampling Rate

- **After every task commit:** `pio run -e uno` (0.5 s warm) + `pio test -e native -f "*test_read_timing*"`
- **After every plan wave:** all three `pio run` + `pio test -e native` + `pio test -e native_nodevtools` + `python3 scripts/check_build_warnings.py`
- **Before `/gsd-verify-work` (phase gate):** cold rebuild of all three targets;
  `check_size_baseline.py --policy merge05 --baseline …base01.json --rebuild`;
  `check_no_heap_or_64bit_symbols.py`; both native envs green; **and** `pytest tests/` in
  `firestarter_app` on a **committed** firmware tree (expect **1976 passed**, or an explained delta)
- **Max feedback latency:** ~20 s (quick), ~50 s (both native envs), ~241 s (host suite)
- **Record:** `.planning/v1.33/157-before-figures.md` and `157-after-figures.md`, per the 155/156 convention

**The size gate is one-sided and this phase is a shrink.** `check_size_baseline.py:697` is
`if flash_delta > allowance` and `:709` is `if ram_delta > ram_tolerance` — growth-only, so a
reduction passes with **no named exemption** (D-03). The canonical `--policy merge05` run fails
with **exactly two lines, both native case counts** — **no AVR flash or RAM leg fails** — so the
pre-existing BASE-01 RED masks nothing. New native cases move the count off 172; that is a
**handoff to Phase 158's LAND-01**, not a defect of this phase.

---

## Per-Task Verification Map

*Task IDs are assigned by the planner; this map is completed at plan time. The requirement→check
mapping below is fixed by research and is what each task must inherit.*

| Task ID | Plan | Wave | Requirement | Behaviour to prove | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|--------------------|-----------|-------------------|-------------|--------|
| TBD | TBD | **0** | all | Before-figures captured and committed **before any edit** — 3 flash/RAM pairs, the eleven-stub ledger summing to **exactly 1012 B**, the five zero-cost siblings absent from the symbol table, `test_read_timing` at 9 cases | measurement | `pio run -e {uno,uno328pb,leonardo}` + `avr-nm --print-size --size-sort --radix=d …elf` | ❌ **W0** | ⬜ pending |
| TBD | TBD | **0** | DECODE-05 | **RED-first** capture, on **TWO** probes — see C-18 below. Probe A (saturation deleted) reddens **S1/S2** while the existing 172 still pass. Probe B (**saturating** bitmask) is the only thing that reddens **S4**. | native planted-negative | `pio test -e native` on each probe tree | ✅ RED direction **already proven** for probe A (F-4: 172/172 green on the broken tree) | ⬜ pending |
| TBD | TBD | **0** | DECODE-05 | Case **S1** — `{"cmd":1,"algorithm":261}` → `h.protocol == 0xFF`; 261 does **not** become 5 | unit | `pio test -e native -f "*test_read_timing*"` | ❌ **W0** | ⬜ pending |
| TBD | TBD | **0** | DECODE-05 | Case **S2** — the **dispatch** fail-closes: `configure_memory` yields `RESPONSE_CODE_ERROR` and not `flash_5v_page`'s main op. **The load-bearing case** — the one that would have caught the defect | unit | same | ❌ **W0** | ⬜ pending |
| TBD | TBD | **0** | DECODE-05 | Case **S3** — `algorithm: 5` still reaches `configure_flash_5v_page` (non-regression, so S1/S2 can't be satisfied by breaking every algorithm) | unit | same | ❌ **W0** | ⬜ pending |
| TBD | TBD | **0** | DECODE-05 | Case **S4** — `{"cmd":2,"flags":65536}` → `h.ctrl_flags == 0` (**MASK**), **never** `0xFFFF`. Encodes F-1 / C-7 / OD-1 | unit | same | ❌ **W0** | ⬜ pending |
| TBD | TBD | **0** | DECODE-05 | Case **S5** — `page-size: 65600` → `0xFFFF` and `eeprom28c_page_mask` falls back; today's truncation to a **valid** 64 is the hole | unit | same | ❌ **W0** | ⬜ pending |
| TBD | TBD | **0** | DECODE-06 | A `read-strobe-us` cap case exists (it does **not** today — C-8), and both knobs assert `== 1000`, not `<= 1000` | unit | same | ❌ **W0** | ⬜ pending |
| TBD | TBD | **0** | DECODE-03 | The `_Static_assert` **is proven able to fire**: reorder a field below `data_buffer` in a throwaway worktree **named `firestarter`**, build must FAIL with the assertion's message, then discard | planted-negative | `pio run -e uno` in the probe worktree | ❌ **W0** | ⬜ pending |
| TBD | TBD | **0** | DECODE-03 | *(closes ceiling 9)* one store-round-trip case per otherwise-untested table field — `mem_size`, `address`, `pulse_delay`, `chip_id`, `vpp_mv`, `pins` | unit | same | ❌ **W0** | ⬜ pending |
| TBD | TBD | 1+ | DECODE-01 | The eleven `get_*` stubs and `key_parsers`' function-pointer column are gone; the five siblings still cost zero | build + symbol ledger | `avr-nm --print-size --size-sort --radix=d …elf \| grep -E 'get_\|FIELDS\|key_parsers'` | ✅ tool exists; **record, not a gate** — ceiling 4 | ⬜ pending |
| TBD | TBD | 1+ | DECODE-01 | **−890 B** table-only and **−1148 B** total on all three targets (ROADMAP's −976/−172 split is wrong — C-3) | two-variant build measurement | `for e in uno uno328pb leonardo; do pio run -e $e; done`, table-only variant then + narrowing | ✅ both variants built this session | ⬜ pending |
| TBD | TBD | 1+ | DECODE-02 | Every wire key appears **once** in flash, on all three targets. **Eleven** of eleven were doubled, not ten (C-4) | ELF string-block diff | `strings -a -n 2 -t d <elf> \| awk '$1>=200 && $1<=560'` | ✅ tool exists; **record, not a gate** — ceiling 4 | ⬜ pending |
| TBD | TBD | 1+ | DECODE-02 | Single-key-storage is a **source property**, not a toolchain accident: `get_flags` references `key_flags` directly (**OD-3 / A6**, 3 lines), then re-measured per target | source + symbol | `grep -rn get_flags src/` + `avr-nm \| grep get_flags` | ✅ | ⬜ pending |
| TBD | TBD | 1+ | DECODE-02 | `get_flags` is still a real function, called from `json_parse_config` **and `json_get_cmd`** — two **different** functions, not two sites in one (C-6) | source + symbol | same | ✅ | ⬜ pending |
| TBD | TBD | 1+ | DECODE-03 | `width` derives from the member (`sizeof(((firestarter_handle_t*)0)->member)`) and a `_Static_assert` prevents a reorder from truncating an offset. **The reference patch guards only `page_size` — all eleven rows need it** (C-9) | **compile-time** | `pio run -e {uno,uno328pb,leonardo} && pio test -e native` — the assertion **is** the test | ✅ verified to compile on all four | ⬜ pending |
| TBD | TBD | 1+ | DECODE-04 | `protocol` is `uint8_t`, `ctrl_flags` is `uint16_t`; no behavioural change | full native suite, both envs | `pio test -e native && pio test -e native_nodevtools` | ✅ 172/172 verified with the change | ⬜ pending |
| TBD | TBD | 1+ | DECODE-04 | **−258 B / −5 B RAM** attributable to the narrowing alone (not −172 — C-3) | two-variant build | table-only variant, then add the narrowing | ✅ | ⬜ pending |
| TBD | TBD | 1+ | DECODE-04 | Flag-bit host parity unaffected; the narrowing is **not wire-visible** | host gate | `pytest tests/test_revision_constants_parity.py -q` | ✅ GREEN verified | ⬜ pending |
| TBD | TBD | 1+ | DECODE-04 | Real site counts are **18 protocol / 20 total** and **40 `is_flag_set` / 59 uses**, not 19/45 (C-5) — the record states the measured numbers | source scan | `grep -rn` per the research's method | ✅ | ⬜ pending |
| TBD | TBD | 1+ | DECODE-06 | `read-settling-delay` still clamps to 1000 through the table's `clamp` column, and `READ_TIMING_MAX_US`'s `#define` is hoisted above the table | unit | `pio test -e native -f "*test_read_timing*"` | ✅ **exists** (`test_read_timing_params.cpp:121`), verified GREEN with the table | ⬜ pending |
| TBD | TBD | 1+ | DECODE-07 | The `switch` alternative is recorded with a measurement taken **at this phase's position** (**OD-4** — the ROADMAP's 25696/25678 absolutes are stale by ~1.4 KB) | measurement, then record | build the `switch` variant once, record the delta, discard | ❌ **W0-adjacent**; ~15 min | ⬜ pending |
| TBD | TBD | 1+ | cross-cutting | The host wire-key parity gate stays green — **OD-2 makes this a zero-edit surface** (F-2) | host gate | `pytest tests/test_json_key_parity.py -q` on a committed tree | ✅ exists; **must be run** | ⬜ pending |
| TBD | TBD | 1+ | cross-cutting | Zero AVR build warnings | build gate | `python3 scripts/check_build_warnings.py` | ✅ exists; **UNVERIFIED this session — OD-6 says run it, don't assume** | ⬜ pending |
| TBD | TBD | 1+ | cross-cutting | Still heap-free and 64-bit-runtime-free (Phase 155 non-regression) | symbol gate | `python3 scripts/check_no_heap_or_64bit_symbols.py` | ✅ exists; **UNVERIFIED this session — OD-6** | ⬜ pending |
| TBD | TBD | 1+ | cross-cutting | No size/RAM regression, recorded as **one-sided** (D-03) | size gate | `check_size_baseline.py --policy merge05 --baseline …base01.json --rebuild` | ✅ | ⬜ pending |
| TBD | TBD | 1+ | cross-cutting | Host suite unchanged | pytest | `python3 -m pytest tests/ -q -o addopts=""` → **1976 passed** or an explained delta | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**The one test-design constraint that will bite if ignored.** `simple_strtoul` returns
`unsigned long` — **32-bit on AVR, 64-bit on native x86-64**. So `store_field`'s
`if (width < sizeof(v))` is `width < 4` on AVR and `width < 8` on native: on native the 4-byte
members saturate too, while on AVR they do not. **Confine DECODE-05's cases to the six narrow
fields and to input values < 2³².** `{"algorithm":261}` is a valid oracle;
`{"memory-size":4294967296}` is not. Consider typing `store_field`'s value `uint32_t` to remove
the divergence outright, and measure the byte cost if so.

---

## Wave 0 Requirements

- [ ] **Before-figures captured and committed before any edit** (`.planning/v1.33/157-before-figures.md`).
      Irrecoverable afterwards, and Phase 158 invalidates them. §Measured Figures of
      `157-RESEARCH.md` is its raw material.
- [ ] **`test/native/avr/test_read_timing/test_read_timing_params.cpp`** — DECODE-05 cases
      **S1, S2, S3, S4, S5**. **S2 is load-bearing**; **S4 encodes F-1 / OD-1**. Author
      **RED-first**, capture the RED, then land the fix and capture GREEN — **but against TWO
      probes, not one (C-18):** probe A (saturation deleted) reddens S1/S2; **S4 passes vacuously
      there** because a narrowed `ctrl_flags` truncates `flags: 65536` to 0, which is what S4
      asserts. S4's only non-vacuous negative is probe B, a **saturating**-bitmask tree that yields
      `0xFFFF`. This is the cheapest possible home: already inside both native `test_filter`
      lists, already includes `json_parser.h` + `jsmn.h`, already has a real `parse_json` helper
      calling `jsmn_parse` with the true token budget, and `configure_memory` is linkable from the
      same env. **A dedicated suite would need both `test_filter` lists AND both `-I` lists updated
      in lockstep** — and would still move the case count.
- [ ] **Same file** — DECODE-06: a `read-strobe-us` cap case (**does not exist today**, C-8) and
      `<=` → `==` tightening on both knobs.
- [ ] **Same file** — one store-round-trip case per remaining table field (`mem_size`, `address`,
      `pulse_delay`, `chip_id`, `vpp_mv`, `pins`), closing **ceiling 9**. **OD-5: take these.** A
      wrong `offsetof` in one row is the refactor's most plausible silent defect, and the case count
      already moves, so six more cost nothing in gate terms.
- [ ] **A planted-negative probe for the `_Static_assert`** — throwaway worktree **named
      `firestarter`** (the name matters: sibling-layout gates key off it), reorder a field below
      `data_buffer`, confirm the build FAILS with the assertion's message, then discard.
      **A never-seen-to-fire assertion is not evidence.**
- [ ] **`.planning/v1.33/157-after-figures.md`** — the after ledger, the corrections index
      **C-1…C-16**, DECODE-07's record, the four operator/orchestrator decisions OD-1…OD-7, and the
      **LAND-01 case-count handoff** to Phase 158.
- [ ] **No framework install needed** — every tool is present and verified.

---

## ⚠ The Honest Coverage Ceilings — stated, not implied

**These must appear, in these terms, in every plan, every SUMMARY, and the phase record.**

1. **`src/json_parser.c` IS natively covered** (F-3) — `build_src_filter` includes
   `+<json_parser.c>`, and `test_read_timing` already drives `json_parse` against a real
   `jsmn_parse`. Every behavioural criterion in this phase is reachable by a native test **that CI
   runs**. **This phase has no coverage gap of Phase 155's kind, and its record must NOT borrow
   that phrasing.** This is the opposite of `rurp_common.cpp`'s situation and saying otherwise
   would be a false ceiling.
2. **`src/firestarter.cpp` and `src/eprom_operations.cpp` are OUTSIDE the native `src_filter`.**
   Between them they hold 8 of the 40 `is_flag_set` uses and the `eprom_block_budget_s` call. The
   narrowing's effect there is proven **only by compilation**, never by execution.
3. **`src/dev_tools.cpp` is outside too** — 9 `is_flag_set` uses plus 7 `LOG_INFO_ID*` expansions,
   the single largest concentration. Compile-only coverage.
4. **DECODE-01 and DECODE-02 have NO automated gate.** They are measurements recorded in
   `157-after-figures.md`. No test asserts that the eleven stubs stayed deleted or that a key is
   stored once. A future phase could silently reintroduce either. **Do not describe them as gated.**
5. **The −5 B RAM saving is unobservable natively** (`sizeof` is 655 either way). AVR-only.
6. **Saturation-as-fail-closed is CONTINGENT on `0xFF` being unmapped** in `configure_memory`'s
   dispatch chain. That is a property of the **dispatch table**, not of `store_field`, it is true
   only today, and it is pinned by **no** test unless case S2 is written. Record it as contingent.
7. **`_Static_assert` proves the offsets fit `uint8_t` at build time — it does NOT prove the table
   writes the right member.** Only the native parse tests do that, and only for the fields they
   exercise (today `read_settling_us`, `read_strobe_us`, `page_size`; after Wave 0 also `protocol`
   and `ctrl_flags`, plus the six round-trip fields if OD-5 is taken).
8. **No bench coverage, by design** (D-02). No criterion needs silicon; nothing here is claimed of
   real hardware.
9. **`check_size_baseline.py` and `check_build_warnings.py` are in NO CI workflow.** Every gate in
   this phase beyond the four CI legs is a **local-run obligation**. A green CI run is not evidence
   that the size gate passed.
10. **The reference patch does not apply cleanly** (C-12): hunk #3 fails at every `-C` level because
    Phase 154's sweep changed its context. The implementation is a hand-port, and the patch is
    evidence, not a shortcut.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The eleven-stub symbol ledger and the single-key-storage string dump | DECODE-01, DECODE-02 | No committed gate exists (ceiling 4); the assertion is a recorded measurement | `avr-nm --print-size --size-sort --radix=d …elf` and `strings -a -n 2 -t d <elf>` before and after, both transcribed into `157-after-figures.md` |
| The `switch`-variant +Δ for DECODE-07 | DECODE-07 | Record-only requirement; the variant is built once and discarded | Build `configure_memory` with a `switch`, record the flash delta on `uno` at this phase's position (OD-4), discard the variant |
| The `_Static_assert` planted-negative | DECODE-03 | Requires a deliberately-broken throwaway tree that must not be committed | Worktree named `firestarter`, reorder a field below `data_buffer`, `pio run -e uno` must FAIL naming the assertion, discard |

*No hardware verification: D-02 — no success criterion in this milestone requires a physical board.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 50s (both native envs)
- [ ] RED-first captured for S1/S2 on probe A **and** for S4 on probe B before the fix lands (C-18)
- [ ] `_Static_assert` seen to fire before it is trusted
- [ ] All ten coverage ceilings restated verbatim in the phase record
- [ ] No task chases the pre-policy −1148 / −890 figures (C-19)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
