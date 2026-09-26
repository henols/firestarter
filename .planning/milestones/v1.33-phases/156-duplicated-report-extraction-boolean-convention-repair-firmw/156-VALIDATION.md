---
phase: 156
slug: duplicated-report-extraction-boolean-convention-repair-firmware-only
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-23
---

# Phase 156 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `156-RESEARCH.md` §Validation Architecture, where every figure below was measured
> at `firestarter` `adf1a31` on a clean tree — **not** carried from ROADMAP.md, several of whose
> figures the research corrects (C-1 … C-7).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | **Unity** (native, PlatformIO `test_framework = unity`) + **pytest 9.1.1** over `firestarter/tests/` (38 modules) |
| **Config file** | `firestarter/platformio.ini` (10 envs; 6 native) |
| **Quick run command** | `pio test -e native` (~21–35 s) |
| **Full suite command** | `pio test -e native && pio test -e native_nodevtools && python3 -m pytest tests/ -q` |
| **Estimated runtime** | ~105 s (21 + 71 + ~13) |
| **CI legs, exhaustively** | `pio test -e native` · `pio test -e native_nodevtools` · `pytest tests/ -v` · `pio run` — `.github/workflows/build.yml:142,155,161,193` and `beta-build.yml:122,128,134,145`. **Nothing else.** |
| **Non-CI local gates** | `pio test -e native_loop_v131` (env comment: "NO CI COVERAGE"), `scripts/check_size_baseline.py`, `scripts/check_build_warnings.py` |
| **Size measurement** | `pio run -e uno -e uno328pb -e leonardo` + `grep -E '^(RAM\|Flash):'` |

**Measured baseline at `adf1a31`, clean tree:**

| Leg | Result |
|-----|--------|
| `pio test -e native` | **172 cases / 17 suites / 172 succeeded**, 21 s |
| `pio test -e native_nodevtools` | **172 / 17 / 172**, 71 s |
| `pio test -e native_loop_v131` (**not in CI**) | **80 / 2 suites / 80 succeeded**, 8 s (`test_loop_eprom_v131` 47 + `test_vpp_eprom_v131` 33) |
| `python3 -m pytest tests/` | **313 passed / 0 failed / 32 skipped** (committed clean tree) |
| `pio run -e uno` | flash **24660**, RAM **1567** |
| `pio run -e uno328pb` | flash **24708**, RAM **1573** |
| `pio run -e leonardo` | flash **26804**, RAM **2008** |
| `tests/golden/protocol_branch_inventory.json` blob-SHA leg | GREEN (`838aca47…` matches) |

**Target after this phase — measured, reproduced on all three targets:** flash
**24234 / 24282 / 26378**, i.e. **−426 B** each, **RAM unchanged**.

---

## Sampling Rate

- **After every task commit:** `pio test -e native` (~21–35 s).
  **Additionally**, for any commit touching `eprom.cpp` or `flash_intel.cpp`:
  `pio test -e native_loop_v131` (~8 s) — it is the **only** suite that executes those VPP paths.
- **After every plan wave:** `pio test -e native && pio test -e native_nodevtools && python3 -m pytest tests/ -q`,
  plus `pio run -e uno -e uno328pb -e leonardo` with the figures recorded.
  Run the pytest leg **only after the firmware commit lands** — `tests/test_flash_path_record_sync.py`
  asserts whole-repo porcelain.
- **For any commit touching `eprom.cpp`:** `python3 -m pytest tests/test_protocol_branch_inventory.py -q`
  **in the same commit** as the re-derived golden (the one-commit property).
- **Before `/gsd-verify-work`:** all eight phase-gate legs green (below).
- **Max feedback latency:** ~21 s (quick) / ~105 s (full).

**Phase gate — all eight must be green:**

1. `pio test -e native` → **172/172, 17 suites**. The count is an **exact-equality** input to
   `compare_native` (`cases == 172`) — strengthen existing cases rather than adding new ones on this leg.
2. `pio test -e native_nodevtools` → **172/172, 17 suites**
3. `python3 -m pytest tests/ -q` → **≥313 passed**, 0 failed — after the firmware commit lands
4. `pio test -e native_loop_v131` → **≥80/80** (its `test_requirement_case_mapping_v131` check is a
   **floor**, so `test_vpp_eprom_v131` is free to grow past 33)
5. `pio run -e {uno,uno328pb,leonardo}` → flash **24234 / 24282 / 26378**, RAM **unchanged**;
   delta recorded against the pre-change same-tree figures above
6. Every new DEDUP-03 assertion seen **RED against its planted transposition** and **GREEN against
   the real tree** — recorded, both directions
7. `python3 scripts/check_size_baseline.py --policy merge05` run, green, and its **one-sidedness
   recorded** (D-03: `if flash_delta > allowance`, so a reduction needs no exemption).
   `size_baseline.json` is **NOT re-anchored** — LAND-01 / Phase 158 owns that.
   ⚠ The canonical invocation is already RED on `beta` for a **pre-existing, unrelated** reason
   (`native: cases baseline=141 observed=172`, BASE-01 frozen at Phase 124). That is Phase 158's
   problem; do not "fix" it here and do not read it as this phase's failure.
8. `scripts/check_build_warnings.py` → no new warning on `eprom.cpp`, `flash_intel.cpp`,
   `flash_utils.cpp`, `eeprom_28c.cpp`, `eprom_operations.cpp`, `operation_utils.cpp`

**Native-suite flakiness (D-04):** never blame a change on N=1. Phase 155 ran the suite seven times.

---

## Per-Task Verification Map

*Task IDs are assigned by the planner; this map is completed at plan time. The requirement→check
mapping below is fixed by research and is what each task must inherit.*

| Task ID | Plan | Wave | Requirement | Behaviour to prove | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|--------------------|-----------|-------------------|-------------|--------|
| TBD | TBD | **0** | all | Pre-change before-figures captured and committed **before any edit** — 3 flash/RAM pairs, `eprom_check_vpp` 524 B, `flash_intel_check_vpp` 562 B, `__udivmodhi4` **31** sites (not 30 — C-2) | measurement | `pio run -e {uno,uno328pb,leonardo}` + `avr-nm --print-size --size-sort -C` + `avr-objdump -d \| grep -cE '(r?call\|jmp).*__udivmodhi4'` | ❌ **W0** | ⬜ pending |
| TBD | TBD | **0** | DEDUP-03 | Under-voltage `(MSG_WARN_VPP_LOW, RESPONSE_CODE_WARNING)` pairing asserted — closes **BLIND SPOT 1** (probe B) | native planted-negative | `pio test -e native_loop_v131` → `test_vpp_eprom_v131` | ❌ **W0** (not CI-visible) | ⬜ pending |
| TBD | TBD | **0** | DEDUP-03 | Chip-ID **message id** asserted (`MSG_WARN_CHIP_ID_MISMATCH` / `MSG_ERR_CHIP_ID_MISMATCH`) — closes **BLIND SPOT 2** (probe D) | native planted-negative | `pio test -e native` → `test_eeprom28c_sdp` / `test_sdp_harness` | ❌ **W0** ⚠ needs an id-capture helper — **verify one exists first (A4)** | ⬜ pending |
| TBD | TBD | **0** | DEDUP-04 | Case 24 polarity assertion flipped (`test_eeprom28c_sdp.cpp:1487`) — **measured RED by construction** | native behavioural | `pio test -e native` | ❌ **W0** | ⬜ pending |
| TBD | TBD | **0** | DEDUP-04 | Case 25 de-vacuumed (`:1524-1534`) — drive loop flipped **and** `calls == 4` asserted. **Measured: passes vacuously taking 1 call** | native non-vacuity | `pio test -e native` | ❌ **W0** | ⬜ pending |
| TBD | TBD | **0** | all | `tests/golden/protocol_branch_inventory.json` re-derived with the module's **own extractor**: `total_sites` 23 → 21, `protocol_keyed_sites` 1 → 1, `other_sites` 22 → 20; two removed, none added; record that the `chip_id` predicate **moved into `memory.cpp`** | pytest source-contract | `python3 -m pytest tests/test_protocol_branch_inventory.py -q` | ⚠ **2 legs RED until re-derived** | ⬜ pending |
| TBD | TBD | 1+ | DEDUP-01 | One `mem_util_report_voltage()` replaces 4 blocks; **8-byte payload length** unchanged | native behavioural | `pio test -e native_loop_v131` → `test_vpp04_a` (`logged_id_param_count == 8`) | ✅ (length only — see ceiling 4) | ⬜ pending |
| TBD | TBD | 1+ | DEDUP-01 | Arithmetic preserved exactly, incl. the `uint16 + 50` promotion — `uint16_t` parameters are **load-bearing** | source contract | comment-stripped scan: extracted expressions character-identical to the four originals; corroborated by `__udivmodhi4` (not `__udivmodsi4`) | ✅ | ⬜ pending |
| TBD | TBD | 1+ | DEDUP-01 | `__udivmodhi4` call sites fall to **13** | mechanical | `avr-objdump -d \| grep -cE '(r?call\|jmp).*__udivmodhi4'` → `13` | ✅ command verified; **no committed gate** | ⬜ pending |
| TBD | TBD | 1+ | DEDUP-01 | No behaviour change on the four VPP paths | native regression | `pio test -e native_loop_v131` (80/80) + `pio test -e native` (172/172) | ✅ both green on the patched tree | ⬜ pending |
| TBD | TBD | 1+ | DEDUP-02 | One `mem_util_report_chip_id()` replaces 4 blocks; the four sites and **six divergences** enumerated and the resolved semantic **stated, not silently chosen** | documentary + native regression | the plan's own record + `pio test -e native` 172/172 | ✅ | ⬜ pending |
| TBD | TBD | 1+ | DEDUP-02 | `response_code` fork preserved | native behavioural | `pio test -e native` → `test_case7_mismatching_chip_id_with_force_warns` (`:803`) + `test_migrated_mismatching_chip_id_errors` (`:619`) — **proven able to fail** by probe C | ✅ exists, **in CI** | ⬜ pending |
| TBD | TBD | 1+ | DEDUP-02 | The standalone `CMD_CHECK_CHIP_ID` path still refuses **unconditionally**, independent of `FLAG_FORCE` (divergence 1) | native behavioural | *no oracle exists* | ❌ **W0** — the one place divergence 1 could silently regress | ⬜ pending |
| TBD | TBD | 1+ | DEDUP-03 | A transposed VPP **over-voltage** `response_code` fails a test | native planted-negative | `pio test -e native_loop_v131` (probe A → 3 RED) | ✅ exists — **NOT in CI** | ⬜ pending |
| TBD | TBD | 1+ | DEDUP-04 | Flip is **size**-neutral on all **three** targets (one more than the survey claimed) | measurement | `pio run -e {uno,uno328pb,leonardo}`, compare `flash_used`/`ram_used` → `0/0` ×3 | ✅ verified | ⬜ pending |
| TBD | TBD | 1+ | DEDUP-04 | 9 `!` gone, 6 engine returns flipped, defensive comment at `eprom_operations.cpp:57-63` removed | source-scan | `grep -c 'return !op_execute_' src/eprom_operations.cpp` → `0`, **plus a non-vacuity leg** | ✅ command verified; **no committed gate** | ⬜ pending |
| TBD | TBD | 1+ | all | No other committed gate regressed | pytest | `python3 -m pytest tests/ -q` → ≥313 passed | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**DEDUP-04 cannot go vacuous — but it nearly did.** `test_eeprom28c_sdp.cpp:1487` (Case 24) fails
**by construction** after the flip, so it cannot be missed. `:1524` (Case 25) **keeps passing** while
taking **1** `op_execute_simple_operation` call instead of the **4** its own comment requires —
proven live with a planted probe (`Expected 4 Was 1`). Flip the assertion; **never delete the case**.

---

## Wave 0 Requirements

- [ ] **Pre-change before-figures, captured and committed before any edit.** Irrecoverable afterwards,
      and Phases 157–158 each invalidate them. Must include the corrected `__udivmodhi4` count of
      **31** (ROADMAP says 30 — C-2).
- [ ] **`test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp`** — the under-voltage
      `(MSG_WARN_VPP_LOW, RESPONSE_CODE_WARNING)` pairing, for both `eprom.cpp` and `flash_intel.cpp`
      if reachable. Closes **blind spot 1**. Env `native_loop_v131`; its gate is a **floor** (≥ 32),
      so adding cases is free. **Not CI-visible — must be recorded as such.**
- [ ] **`test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` and/or `test_sdp_harness.cpp`** —
      chip-ID **message-id** assertions added to the two cases that already assert `response_code`.
      Closes **blind spot 2**, **in CI**, and keeps `cases == 172` by **strengthening rather than adding**.
      ⚠ **Requires an id-capture helper in those suites' stubs — grep for one FIRST (open question A4,
      the plan's biggest shape risk).** `test_vpp_eprom_v131`'s `count_logged_id` lives in its own
      `host_stubs.cpp` and may not be shared.
- [ ] **`test_eeprom28c_sdp.cpp:1487`** — Case 24's polarity assertion **must** flip
      (`TEST_ASSERT_FALSE` → `TEST_ASSERT_TRUE`) with its message rewritten. Measured RED.
- [ ] **`test_eeprom28c_sdp.cpp:1582-1590`** — Case 25's drive loop **must** be flipped and a
      `calls == 4` assertion added. Measured: passes vacuously after the flip.
- [ ] **`tests/golden/protocol_branch_inventory.json`** — re-derive with the module's own extractor
      (23 → 21 sites), in the **same commit** as the `eprom.cpp` edit.
- [ ] *(optional, high value)* **a source-scan gate for DEDUP-04** — the only mechanical check possible
      on a TU that compiles in **no** native env. Follow `tests/test_write_path_source_contract_v131.py`'s
      idiom. ⚠ **Must be non-vacuous:** a zero-match grep passes trivially against a deleted file, so
      pair it with a non-vacuity leg. The project has been bitten by exactly this.
- [ ] *(optional)* **a `mem_util_report_voltage` payload-value oracle**, closing ceiling 4. Not required
      by any criterion; recorded so the gap stays visible.

**Framework install: none needed** — everything is present and verified. Use system `python3 -m pytest`,
not the pio penv.

---

## ⚠ The Honest Coverage Ceilings — stated, not implied

**These must appear, in these terms, in every plan, every SUMMARY, and the phase record.**

1. **`src/eprom_operations.cpp` compiles in NO native environment.** All native envs share
   `build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>`.
   The nine dropped `!` therefore have **no behavioural oracle** — only the size-identity build and
   source inspection. `src/operation_utils.cpp` **is** in the filter, so the **6 flipped returns** are
   covered, by Cases 24/25 **and nothing else**. No phase artifact may imply native coverage of the wrappers.
2. **`test_vpp_eprom_v131` and `test_flash_intel_vpp` are in no CI leg.** The former runs only under
   `native_loop_v131`, whose own comment says "**NO CI COVERAGE**". The latter is in **no env's
   `test_filter` at all** — KNOWN-FLAKY, disabled since Phase 17, its SAF-04 assertions "have never
   been observed to execute". So the entire `flash_intel.cpp` VPP path — **two of DEDUP-01's four
   blocks** — has **zero executing test coverage in any environment**. Its regression evidence is the
   `eprom.cpp` twin's, plus the source-level byte-identity of the two blocks.
3. **The AVR 16-bit promotion is unobservable natively.** Native `int` is 32-bit, so no native test can
   attest the AVR arithmetic or its wrap above 65485 mV. Identical before and after; not a regression;
   **not covered**.
4. **The 8-byte payload's byte *values* have no oracle anywhere.** `test_vpp04_a` asserts the **length**
   is 8. Criterion 1's "the emitted 8-byte payload is unchanged" is established by **source-level
   identity of the arithmetic** (extracted expressions character-identical to the four originals,
   parameter types identical) plus the length assertion — **not by a value comparison**. Say so; do not
   let the record read as if the bytes were compared.
5. **`scripts/check_size_baseline.py` runs in no CI workflow at all** (LAND-04). Every size gate here is
   a **local-run obligation**.
6. **No bench claim** (D-02). Nothing in this phase is attested on silicon.
7. **DEDUP-04's "byte-for-byte zero" is a SIZE claim, not an IMAGE claim.** The `.hex` SHA **changes on
   all three targets** and `avr-objdump` differs on **5450 lines** — a uniform +2 B relocation plus
   `brne`↔`breq` swaps. The build was proven reproducible first, so this is a real negative result.
   **An oracle asserting image identity would go RED.** ROADMAP criterion 4's "byte-for-byte" wording
   is corrected by C-4; the claim that may be made is *size*-identity on all three targets.

**Forbidden phrasings** in any Phase 156 artifact: *"byte-for-byte identical image"* for the DEDUP-04
flip; *"the payload bytes were compared"* for DEDUP-01; *"covered by CI"* for anything living only in
`native_loop_v131`; *"tested"* / *"verified on hardware"* / *"bench-verified"* for the wrapper flip.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | — | — |

**All phase behaviors have automated verification**, with two stated exceptions that are *documentation
obligations*, not manual tests:
- **DEDUP-02** — the *statement* of the resolved single semantic across the six divergences is itself
  the deliverable; the code change is covered by the native regression and the `response_code` fork tests.
- **DEDUP-04's decline branch** — dead. OD-2 resolved it toward **removal**, so there is nothing to
  document in lieu of a change.

**No bench/hardware leg exists in this phase, by decision (D-02), and none may be implied.**

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (6 required + 2 optional above)
- [ ] Both DEDUP-03 blind spots closed, each seen **RED against its planted transposition** and GREEN against the real tree
- [ ] Case 24 flipped and Case 25 **de-vacuumed** with `calls == 4` — the vacuity was measured, not hypothesised
- [ ] `protocol_branch_inventory.json` re-derived with the module's own extractor, in the same commit as the `eprom.cpp` edit, with the `memory.cpp` move recorded
- [ ] Native case count still **172 / 17 suites** on both CI native legs — `compare_native` asserts exact equality
- [ ] No watch-mode flags
- [ ] Feedback latency < 21 s (quick) / 105 s (full)
- [ ] `size_baseline.json` **not** re-anchored (LAND-01 / Phase 158 owns it)
- [ ] No forbidden coverage phrasing in any Phase 156 artifact
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
