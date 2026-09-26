# Phase 140: Parameter Table - Research

**Researched:** 2026-08-09
**Domain:** AVR/C++ embedded const-table design (PROGMEM), PlatformIO native test plumbing, committed source-scan gates, primary EPROM datasheet attribution
**Confidence:** HIGH (code/infrastructure findings measured in-tree this session); HIGH for `0x08`/`0x0B` datasheet attribution; MEDIUM for `0x07`'s `overprogram_factor` provenance

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: The table ships SIX columns — the five TABLE-01 names, plus `energy_cap_us`.**
  `energy_cap_us` = `0` on `0x07` and `0x08` (no cap), `50000` on `0x0B`. TABLE-01 says the table
  "carries rows … with" those five columns; it does not say *only* those five, so a sixth is
  additive rather than a violation and needs no REQUIREMENTS amendment.
  **Rationale:** LOOP-04 requires "accumulated program time per byte capped at 50 ms" on `0x0B`, and
  none of the five named columns can express it. A dedicated column is self-documenting, gives
  TABLE-04 one cell to cite, and lets Phase 141's loop read it like every other column.
  *Rejected:* deriving `max_pulses = 50000 / pulse_delay`; overloading `overprogram_cap_us`; keeping
  the cap as an `if (protocol == PROTO_EPROM_24PIN)` inside Phase 141's loop.

- **D-02: `verify_mode` encodes WHEN to verify, never at what VCC.** Two values:
  `VERIFY_PER_PULSE` (read the byte back after every pulse; this is what drives the loop's exit) and
  `VERIFY_PER_PULSE_PLUS_FINAL` (the same, plus one full-array read-back pass after the block
  completes). Which row gets which is a TABLE-04 research question against the primary datasheets.
  **Hard constraint attached to this column:** it may **never** encode a verify VCC margin. The
  datasheets specify verify at raised VCC for threshold margin; the RURP has no VCC-raise path (the
  ~6.25 V ceiling), so such a column could only record a value the firmware cannot act on. The
  citation for this column must say so explicitly.
  *Rejected:* a single constant value across all three rows; encoding verify VCC.

- **D-03: The `pulse_delay == 0` fallback constants STAY in `configure_eprom`'s switch
  (`eprom.cpp:71-76`) — no pulse number enters the table.** Literal compliance with TABLE-02 and with
  milestone D-01. A column named `fallback_pulse_us` *is* a pulse-width column on any plain reading,
  and gh#15's correction — posted publicly in Phase 139 — just told the world the table has no pulse
  column. Keeping the fallback visibly a fallback also stops a reader mistaking it for the
  algorithm's pulse.
  *Rejected:* a `fallback_pulse_us` column plus a REQUIREMENTS amendment; moving the constants to
  named `#define`s beside the table.

- **D-04: Storage is `PROGMEM`, and this is forced, not preferred.** MERGE-05 requires AVR RAM delta
  **exactly 0** against Phase 138's baseline. On AVR a `const` struct array without `PROGMEM` lands
  in `.data` and is copied into RAM at startup, so a plain `const` table fails the gate on arrival.
  Follow the existing precedent: `static const key_parser_t key_parsers[] PROGMEM` at
  `firestarter/src/json_parser.c:164`. Uno-class flash headroom is **42 B (`uno`) / 36 B
  (`uno328pb`)** against the 64 B MERGE-05 band at the fork base — and materially less at the live
  `beta` tip (F-138-02: 8 B / 2 B). Budget accordingly.

- **D-05: A lookup that finds no row returns NULL and the caller fails closed, with zero hardware
  side effects.** Matches the firmware's standing fail-closed invariant (`memory.cpp` steps 6a/6b/7,
  Phase 64 / v1.20). `configure_eprom` is only reachable with `0x07`/`0x08`/`0x0B` today, but the
  guard survives a future dispatch edit the compiler cannot catch.
  *Rejected:* falling back to the `0x07` row; a compile-time-only `static_assert`.

- **D-06: `0x08`'s `overprogram_factor` goes to research, and the prose wins on a tie.**
  `PROJECT.md` contradicts itself: its prose says overprogram is *"not for Quick-Pulse / Flashrite /
  PRESTO, so it is gated per row"* while its own throughput table gives `0x08` a `3 × N × pulse`
  overpulse. `0x08` is `EPROM_QUICK` in the firmware and its modal DB pulse is 100 µs (n=127) —
  both point at Quick-Pulse. Phase 140's researcher resolves it from the primary
  AM27C020 / 27C010-class datasheets. **If the datasheets are ambiguous or unobtainable, factor 0
  ships** — the asymmetry is that an unneeded 3×N overpulse damages silicon, while a missing one
  merely under-programs and is caught by verify. Either outcome ships with the citation that decided
  it, and **the contradiction itself is named explicitly in the phase record**, not silently
  resolved.
  *Rejected:* deciding it now from either planning document; splitting `0x08` into more than one row
  — though if research finds the 32-pin family genuinely spans both Intelligent and Quick-Pulse
  silicon, that is a **finding for Phase 146**.

- **D-07: On `0x0B`, `max_pulses` and `energy_cap_us` BOTH bind — whichever trips first.**
  `energy_cap_us = 50000` is the intended budget and normally binds; `max_pulses` is a generous
  structural backstop that guarantees termination at a pathological pulse width (Phase 143's
  `--pulse-us 1` would otherwise mean 50 000 iterations on a single byte). Either trip is the same
  LOOP-05 hard-fail, and the error reports **which** limit tripped. TABLE-04 cites the cap to the
  2716-class datasheet and marks `max_pulses` on this row `"no datasheet basis — reasoned from:
  termination bound"`.
  *Rejected:* energy-cap-only with `max_pulses = 0` as a sentinel; count-only.

- **D-08: `overprogram_cap_us = 75000` on both overprogramming rows, and the cap CLAMPS.** The
  overpulse is `min(3 × N × pulse, cap)`. 75 ms is `3 × 25 × 1000 µs`, the Intelligent worst case,
  and is the exact figure C3 was publicly stated against on gh#15 ("the 32-bit-safe helper is needed
  for the 75 ms overprogram pulse") — keeping it uniform keeps that public statement true. On `0x08`
  at the modal 100 µs it never binds; it exists as a hardware-safety ceiling against a large DB pulse
  or a `--pulse-us` override (the minipro wire field is uint16, so 65535 µs is reachable —
  `3 × 25 × 65535 ≈ 4.9 s` without a cap). Cited as **reasoned**, not datasheet-derived.
  *Rejected:* hard-failing instead of clamping; per-row caps.

- **D-09 (Claude's call, delegated): a row's citation is TWO-PART, with an explicit scope clause.**
  Each row cites **(a)** the vendor algorithm family by name — Intel Intelligent Programming, Intel
  Quick-Pulse, classic 2716 50 ms programming — because that is what `protocol_id` actually names,
  and **(b)** one named representative part: manufacturer, part number, datasheet revision/date,
  chosen to be a part Phase 145 can actually bench (`0x07` → W27C512 / TMS27C512, the *required*
  bench coverage; `0x08` → AM27C020; `0x0B` → M2716 / M2732). Every citation carries the literal
  scope sentence: *"representative of this row; not asserted true of all N chips carrying this
  `protocol_id`."*
  *Rejected:* enumerating every distinct value across all 329 chips.

- **D-10: Phase 140 ships DATA + GATES + TEST only. `eprom.cpp` is byte-unchanged.**
  `native_trace_v131` asserts **full ordered positional equality** against Phase 138's frozen trace
  for all three protocols; leaving `eprom.cpp` alone keeps it GREEN through this phase, so the first
  legitimate trace movement is Phase 141's — diffed deliberately in Phase 144 / TEST-06.
  *Rejected:* rewiring the duplicated `0x0B || FLAG_VPE_AS_VPP` VPP branch at `eprom.cpp:145` and
  `:218` now; rewiring **and** re-freezing the fixture inside Phase 140.

  **Consequence the planner must carry:** the table is unreferenced by `src/`, so
  `eprom_params_for()` and the table are garbage-collected out of the AVR image. **Phase 140's AVR
  flash delta is therefore expected to be ~0, and the real flash cost lands in Phase 141.** State
  that expectation explicitly in the phase record. Do **not** force a reference with
  `__attribute__((used))`.

- **D-11: The TABLE-03 fallback test runs in a FIFTH dedicated native env, on the
  `native_trace_v131` precedent.** Both pinned envs (`native`, `native_nodevtools`) are asserted at
  **exactly 141 cases / 17 suites** by the live `scripts/baseline/size_baseline.json`, and
  `check_size_baseline.py`'s default mode is strict byte-identity. The new env names **only** its own
  suite in `test_filter`, is never folded into either pinned env's `test_filter`, and is never added
  to `default_envs`.
  **Known cost, inherited from finding F-138-05 and accepted, not fixed:** `check_size_baseline.py`
  hardcodes `NATIVE_ENVS = ("native", "native_nodevtools")` and `compare_native` does a bare
  dictionary lookup, so an unknown env name raises an **uncaught KeyError (exit 1)**. Both live gates
  are therefore blind to the new env. **The suite must be run explicitly, by name, in this phase's own
  verification**, and its counts recorded in the v1.31 baseline record.
  *Rejected:* adding the test to `test_val_eprom` and re-baselining the live `size_baseline.json`;
  folding it into `native_trace_v131`'s suite.

- **D-12: TABLE-05 splits into TWO gates, each committed in the repo it can actually see.** The
  firmware half lands in `firestarter/`; the `chip_database.json` half lands in `firestarter_app/`.
  Neither needs a cross-repo path seam, so neither can fail open when the other repo moves.
  **Planner consequence:** Phase 140 is dual-repo — `commits_land_in:` names both submodules. The
  DB-half gate is scheduled **here**, not deferred to Phase 143.

- **D-13: The firmware half asserts a PINNED INVENTORY of protocol-branch sites, with an allowlist.**
  The gate enumerates every site in the EPROM path that branches on `handle->protocol` — today:
  `configure_eprom`'s pulse fallback switch (`:71-76`), `eprom_write_execute` (`:145`),
  `eprom_check_vpp` (`:218`), plus the new table — and pins that inventory. A **new** branch site, or
  a branch keyed on **any other** handle field, fails the gate.
  *Rejected:* asserting only that no second protocol-**keyed data structure** exists; pinning
  `memory.cpp`'s dispatch chain.

- **D-14: TABLE-04's citations live in a MACHINE-READABLE SIDECAR, gate-enforced; the C table carries
  short comments pointing at it.** One entry per `(row, column)` cell — family, representative part,
  datasheet revision, the D-09 scope clause, or the `"no datasheet basis — reasoned from X"` form. A
  gate asserts the entry set **exactly** covers the table's cells: every value cited, and no citation
  for a value that does not exist.
  *Rejected:* inline C comments only; a prose markdown doc only.

- **D-15 (house rule, restated because it binds here): every gate this phase authors must be SEEN TO
  FAIL on a planted violation before any pass is believed.** Three specific traps this project has
  already hit: (1) `check_permitted_claims.py`'s `_HERE` resolved to the **checker's own** phase
  directory — any new checker must resolve its targets explicitly and assert it scanned a non-zero
  number of files; (2) a **pre-authored gate leg can be unreachable** — a RED proves nothing until
  the leg has also been seen to pass; when fixing, fix the locator, not the assertion; (3) a planted
  break must be placed where the gate can actually reach it.

### Claude's Discretion

- C types and widths per column (`uint8_t` vs `uint16_t` vs `uint32_t`), and the struct's field
  order — subject to D-04's PROGMEM requirement and the Uno-class flash band.
- File layout: whether the table lives in a new `include/eprom_params.h` + `src/proms/eprom_params.cpp`
  pair or header-only, and how the new native env's `-I` and `test_filter` entries are named.
- Whether `vpp_path` names abstract enum values or raw control-register masks. Phase 142 owns the
  mask sets, so prefer whichever leaves 142 the freer hand.
- `eprom_params_for()`'s exact signature, and whether it returns a `PROGMEM` pointer or copies the
  row out — subject to the RAM-delta-zero constraint.
- `max_pulses` for `0x07` and `0x08` (`PROJECT.md` says 25 for both) and `0x0B`'s backstop figure —
  research-settled under TABLE-04, not asserted from planning prose.
- The sidecar citation file's format and exact path, and the DB-half gate's frozen key-inventory
  form (generated vs hand-written).
- Plan and wave structure. The natural shape is: table + citations → the two TABLE-05 gates (each
  planted-failed first) → the fifth native env + the TABLE-03 fallback test → phase record.

### Deferred Ideas (OUT OF SCOPE)

- **Wiring the table into `eprom.cpp`** — Phase 141 (the loop) and Phase 142 (the VPP branch at
  `:145`/`:218`). D-10 keeps this phase's `eprom.cpp` byte-unchanged.
- **Removing `program_mismatched_bytes()` / `verify_and_update_mask()` / `NUMBER_OF_RETRIES` / the
  adaptive growth formula** — LOOP-02, Phase 141.
- **The 32-bit-safe delay helper** — LOOP-07, Phase 141.
- **`--pulse-us` bounds and pre-validation** — HOST-01…05, Phase 143.
- **Re-baselining `native_trace_v131` and reconciling the flash/RAM delta** — TEST-06 / TEST-08,
  Phase 144.
- **A possible `0x08` family split** — recorded as a finding for Phase 146, never forced into a wrong
  single value here (D-06).
- **Fixing F-138-05** (`check_size_baseline.py`'s uncaught KeyError on an unknown native env) —
  inherited, accepted, not fixed. Owner `henols`.
- **All six todos** from `todo.match-phase 140` — reviewed, not folded (CONTEXT `<deferred>`).
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description (verbatim, `REQUIREMENTS.md:169-179`) | Research Support |
|----|---------------------------------------------------|------------------|
| **TABLE-01** | A `const` table keyed by `protocol_id` carries rows for `0x07`, `0x08` and `0x0B` with `max_pulses`, `overprogram_factor`, `overprogram_cap_us`, `verify_mode` and `vpp_path`. | §Standard Stack (PROGMEM precedent, verified struct layout that is 12 B on **both** AVR and x86-64); §Code Examples (worked header); §Pitfall 1 (the `.cpp` warning trap that constrains file layout). |
| **TABLE-02** | The table has **no pulse-width column** — program pulse width is read from `handle->pulse_delay` on every write path. | §Architecture Patterns (the pulse plumbing, host → wire → `json_parser.c:503` → `handle->pulse_delay`); §Validation Architecture (a name-set gate that is *not* fooled by `max_pulses` containing the substring "pulse"). |
| **TABLE-03** | A protocol's constant pulse is consulted **only** when `handle->pulse_delay == 0`, and that fallback is exercised by a test rather than asserted. | §Architecture Patterns (`configure_eprom` is reachable natively with zero hardware side effects — proven by `test_val_eprom`'s negative controls); §Finding F-140-04 (**0 of 329 shipped 27C chips yield `pulse_delay == 0` — the fallback is unreachable on the bench, so the native test is the only oracle**); §Pitfall 4 (the global handle never resets `pulse_delay`). |
| **TABLE-04** | Every value in every row is cited to a named primary datasheet, or carries an explicit "no datasheet basis — reasoned from X" note. No unattributed number ships. | §Datasheet Attribution Matrix — 8 primary datasheets read this session, per-cell verdicts, plus the three cells with no datasheet basis and the exact wording each needs. |
| **TABLE-05** | No new `chip_database.json` field and no second firmware algorithm selector is introduced — `protocol_id` remains the sole dispatch key, verified by a gate rather than by inspection. | §Architecture Patterns (the complete, measured branch-site inventory including the **two pre-existing non-protocol branches the gate must allowlist or be RED on arrival**); §Standard Stack (the exact DB key inventory, 746 chips); §Validation Architecture (gate placement, CI legs, planted-failure obligations). |
</phase_requirements>

---

## Summary

Phase 140 is a **data + gates + test** phase in a tree that is unusually well instrumented and
unusually tightly constrained. Almost every hard question has a measurable answer in-tree, and this
session measured them rather than reasoning about them. Three findings dominate planning:

**1. File layout is close to forced, for a reason nothing in CONTEXT.md anticipated.** The native
build emits exactly **14 ArduinoFake macro-redefinition warnings per translation unit** that includes
both `<Arduino.h>` and the `avr/pgmspace.h` shim, and `check_build_warnings.py`'s watermark for
`native` / `native_nodevtools` is `<= 1166` sitting **exactly at 1166 with zero headroom**. Because
`build_src_filter = +<proms/>` is shared by all five native envs, a new `src/proms/eprom_params.cpp`
that follows the house include style (`#include <Arduino.h>` + `firestarter.h`, as every other
`src/proms/*.cpp` does) adds +14 warnings to both pinned envs and turns a live gate RED. The escape
is precise and verified: `src/proms/not_implemented.cpp` includes `firestarter.h` but **not**
`<Arduino.h>`, and emits **zero** such warnings. So a `.h`+`.cpp` pair is viable — provided the
`.cpp` never includes `<Arduino.h>`. A dependency-free header (`<stdint.h>` +
`rurp_platform_compat.h` only) plus an `<Arduino.h>`-free `.cpp` satisfies both this constraint and
the `vpp_path` discretion item (abstract enum, no `rurp_shield.h` coupling), leaving Phase 142 free.

**2. The datasheet attribution is far stronger than the milestone record assumed, and it settles
D-06 decisively.** Eight primary datasheets were read this session (five recovered from the repo,
two fetched, one rendered from a scanned PDF). **`0x08`'s `overprogram_factor` is 0**: ST's
M27C1001 (27C010-class, the exact part D-06 names) states verbatim *"No overprogram pulse is applied
since the verify in Margin mode provides necessary margin to each programmed cell"*; AMD's Am27C020
Flashrite description contains no overprogram step; Winbond's W27C020 flowchart has none. That
agrees with `PROJECT.md`'s prose and contradicts its own throughput table — exactly the contradiction
D-06 exists to name. Separately, **`max_pulses = 25` is directly datasheet-attributable** (Winbond
W27C512 Rev A4 "X = 25?", ST M27C512 Fig. 4 "++n = 25", ST M27C1001 Fig. 5, Winbond W27C020), and
**`energy_cap_us = 50000` has a *primary datasheet* basis, not merely a reasoned one**: TI's TMS 2516
specifies `t_w(PR)` = **45 / 50 / 55 ms** (min/typ/max) for the program pulse. That same datasheet
also shows the *justification sentence* published on gh#15 ("100 × 500 µs is the classic 2716 total
programming time") is factually wrong — the 2516's total programming time for all bits is **100
seconds**; 50 ms is the per-location pulse. The value is right; the reason given for it is not.

**3. Two pre-existing non-protocol branches sit inside the EPROM path, and D-13's gate is RED on
arrival unless they are explicitly allowlisted.** `is_flag_set(FLAG_VPE_AS_VPP)` at `eprom.cpp:145`
and `:218` branches on `handle->ctrl_flags`; `using_p1_as_vpp(handle)` at `eprom.cpp:320` branches on
`handle->pins` **and** `handle->bus_config.vpp_line`. Both are hardware-routing predicates, not
algorithm selectors — but D-13's stated rule ("a branch keyed on **any other** handle field fails the
gate") cannot tell the difference. The gate must carry a reasoned allowlist naming all three sites,
or it can never be seen to pass.

**Primary recommendation:** ship a dependency-free `include/eprom_params.h` (types + enums + extern
declaration) paired with an `<Arduino.h>`-free `src/proms/eprom_params.cpp` (the PROGMEM table +
accessor); field-order the struct `uint32, uint32, uint8×4` so `sizeof` is 12 on AVR *and* x86-64;
put both TABLE-05 gates and the TABLE-04 citation-coverage gate in the two repos' existing
CI-executed `tests/` directories on the `test_golden_trace_identity_eprom_v131.py` pattern (standalone
pytest + committed inventory JSON) rather than as `scripts/check_*.py` — which would drag in
`test_checker_convention.py`'s FLOOR/FIXTURE_FLOOR obligations; and add the fifth env
`native_params_v131` as a verbatim copy of `[env:native_trace_v131]`'s shape.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Per-protocol algorithm *shape* (`max_pulses`, `overprogram_*`, `verify_mode`, `vpp_path`, `energy_cap_us`) | Firmware — new `eprom_params` TU | — | Milestone D-01: protocol owns shape. Firmware is the only tier that runs the loop. Keyed by `protocol_id`, which arrives on the wire as the `algorithm` JSON field. |
| Per-chip program **pulse width** | Host DB (`chip_database.json`) → wire → `handle->pulse_delay` | Firmware fallback switch (`eprom.cpp:71-76`) only when the wire value is 0 | Milestone D-01 / C2: the database owns the pulse. TABLE-02 forbids any firmware table column for it. |
| Protocol → handler dispatch | Firmware `memory.cpp:95-138` | — | Sole dispatch key (v1.20). Explicitly **out of scope** for D-13's gate (its "rejected" option) — pinning it would pass even if 140 added a selector inside `eprom.cpp`. |
| "No second algorithm selector" enforcement | Firmware repo `tests/` (CI: `pytest tests/ -v`) | — | D-12: an app-side gate scanning firmware source is the shape that failed open 4× in Phase 117. |
| "No new `chip_database.json` field" enforcement | Host repo `tests/` (CI: `pytest tests/`) | — | D-12: the file lives in the app repo; the gate must live where it can see it without a cross-repo path seam. |
| Per-cell citation coverage | Firmware repo (sidecar + gate co-located with the table) | — | D-14: a citation that can drift from its value is not a citation. Co-location makes the drift a single-commit concern. |
| Fallback-path behavioural proof | Firmware native test (fifth PIO env) | **Nothing else can** — see F-140-04 | 0 of 329 shipped 27C chips produce `pulse_delay == 0`; no bench run can reach this path. |
| Trace/size/warning baselines | Firmware `scripts/` + `tests/` | — | Frozen by Phase 138; Phase 140 must leave them numerically unmoved (D-10). |

---

## Standard Stack

This phase adds **no external packages** to either repo. The "stack" is the toolchain and in-tree
infrastructure already pinned by Phase 138's baseline.

### Core

| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| PlatformIO Core | 6.1.19 | Build + native test runner | Pinned in `size_baseline_v131.json:meta.platformio_core`; present and working in this devcontainer (`/usr/local/bin/pio`) `[VERIFIED: run in-session]` |
| `platform-atmelavr` | 5.2.0 | AVR targets | `size_baseline_v131.json:meta.platform_atmelavr` `[VERIFIED]` |
| `avr-gcc` | 7.3.0 (`toolchain-atmelavr` 1.70300.191015) | AVR compiler | `size_baseline_v131.json:meta` `[VERIFIED]` |
| `framework-arduino-avr` | 5.3.0 / MiniCore 3.1.2 | Arduino core (uno / uno328pb / leonardo) | `size_baseline_v131.json:meta` `[VERIFIED]` |
| Unity | 2.6.1 (`throwtheswitch/Unity@^2.6.1`) | Native test framework | Auto-installed by PIO on `pio test` `[VERIFIED: installed during this session's run]` |
| ArduinoFake | 0.4.0 (`fabiobatsilva/ArduinoFake@^0.4.0`) | Arduino mocking in native envs | `platformio.ini` `lib_deps`, every native env `[VERIFIED]` |
| `PROGMEM` / `pgm_read_*` | AVR libc; shimmed on host | Flash-resident const storage | `include/rurp_platform_compat.h:19-84` supplies `PROGMEM`, `pgm_read_byte/word/dword/ptr`, `memcpy_P` on non-AVR; `include/avr/pgmspace.h` `#include_next`s the real header on AVR `[VERIFIED: read in-tree]` |

### Supporting

| Component | Location | Purpose | When to Use |
|-----------|----------|---------|-------------|
| `static const … PROGMEM` array | `src/json_parser.c:164` (`key_parsers[]`) | The in-tree PROGMEM-table precedent D-04 names | Model for the new table's storage + `pgm_read_ptr` access idiom |
| `_shared/host_stubs_common.inc` | `test/native/avr/_shared/` | Shared `rurp_*` stubs, three opt-in recorder layers | A new suite `#define`s its opt-ins **before** the include (guards read at include time) |
| `[env:native_trace_v131]` | `platformio.ini:293-328` | Complete worked 4th-env instance | Template for D-11's fifth env, including the HARD CONSTRAINT comment block |
| `tests/test_golden_trace_identity_eprom_v131.py` | firmware repo | Standalone pytest + committed inventory JSON, CI-run | **The recommended gate pattern** for D-13/D-14 — see §Don't Hand-Roll |
| `tests/golden/*.json` | firmware repo | Committed inventory records | Where a new pinned inventory belongs |
| `tests/scan_paths.py` | app repo | "Deliberately explicit, never derived" inventory discipline | Model for the DB-half key inventory |
| `tools/diff_db.py` (GATE-02) | app repo | Existing DB drift gate | **Already detects a new field** (`_diff_field_paths` unions both key sets, `diff_db.py:373-392`) — but is silenceable by re-baselining, so it is corroboration, not the TABLE-05 gate |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pytest module in `tests/` (firmware) | `scripts/check_eprom_params.py` | Triggers `tests/test_checker_convention.py`: requires a paired `tests/test_check_eprom_params.py`, at least one `tests/fixtures/planted_eprom_params*` entry, the checker's exact filename inside the test module, a `returncode != 0` assertion, **and** raising both `FLOOR` (6→7) and `FIXTURE_FLOOR` (15→16) in the same commit. All verified at `tests/test_checker_convention.py:127-131, 165-200`. Heavier, but it is the house convention for *executable checkers*; D-15's planted-failure requirement is satisfied either way. |
| Header-only table | `.h` + `.cpp` pair | Header-only duplicates the array per including TU (fine while only `eprom.cpp` includes it; a second includer in Phase 142 would double the PROGMEM cost). The pair gives one copy and one clean Phase-141 seam. **Both are safe only if no `<Arduino.h>` include is added** — see Pitfall 1. |
| Abstract `vpp_path` enum | Raw `rurp_register_t` masks | Masks force `rurp_shield.h` into the header (coupling + Phase 142's mask sets locked early). CONTEXT explicitly prefers "whichever leaves 142 the freer hand" → enum. Also keeps the header dependency-free, which is what makes the `.cpp` `<Arduino.h>`-free. Two constraints converge. |
| `uint32_t overprogram_cap_us` | `uint8_t overprogram_cap_ms` (75) | Halves the struct (12 B → 6 B/row). Rejected: TABLE-01 names the column `overprogram_cap_us` and D-01 names `energy_cap_us`; a `_us`-named field storing ms is exactly the "field that means two things" D-01 rejects. Also 75000 > `UINT16_MAX` (65535), so `uint16_t` is not an option. |

**Installation:** none. No `npm`/`pip`/`cargo` package is added by this phase.

---

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages in either repository.**

| Package | Registry | Disposition |
|---------|----------|-------------|
| *(none)* | — | Phase 140 adds C/C++ source, JSON sidecars, Python test modules and `platformio.ini` entries only. Unity 2.6.1 and ArduinoFake 0.4.0 are pre-existing pinned `lib_deps`, already present in the frozen baseline. |

**Packages removed due to slopcheck [SLOP] verdict:** none — no package set to check.
**Packages flagged as suspicious [SUS]:** none.

---

## Architecture Patterns

### System Architecture Diagram

```
┌─ HOST (firestarter_app) ────────────────────────────────────────────────────────┐
│                                                                                  │
│  infoic.xml ──build_db.py──> chip_database.json   [GENERATED — never hand-edited]│
│                                    │                                             │
│                                    │ programming.pulse_duration ("100 us" | …)   │
│                                    ▼                                             │
│                     database.py:128 _parse_pulse_duration()                      │
│                        "100 us" → 100 ;  "" | "Algorithm Controlled" → 0         │
│                                    │                                             │
│                     database.py:417  data["pulse-delay"] = <int µs>              │
│                     database.py:555  programmer_data["pulse-delay"]  (always)    │
│                     database.py:552  programmer_data["algorithm"] = protocol_id  │
│                                    │                                             │
└────────────────────────────────────┼─────────────────────────────────────────────┘
                                     │  JSON @250000 baud   {"algorithm":7,"pulse-delay":100,…}
┌─ FIRMWARE (firestarter) ───────────▼─────────────────────────────────────────────┐
│                                                                                  │
│  json_parser.c:164  key_parsers[] PROGMEM ──> get_algorithm → handle->protocol    │
│                                          └─> get_delay     → handle->pulse_delay │
│                    ⚠ json_parse() does NOT reset pulse_delay (json_parser.c:164-278)│
│                                    │                                             │
│                    memory.cpp:115  protocol ∈ {0x07,0x08,0x0B} ─> configure_eprom│
│                                    │                                             │
│              eprom.cpp:41  configure_eprom()                                     │
│                 ├─ :46-64  cmd → operation_{init,main,end}                       │
│                 ├─ :66-67  install eprom_internal_set_control_register           │
│                 └─ :70-76  if (pulse_delay == 0) switch(protocol){0x08→100,      │
│                             0x0B→500, default→1000}          ◀── TABLE-03 target │
│                                    │                                             │
│   ╔════════════════════════════════╪═══════════════════════════════════════════╗ │
│   ║ PHASE 140 ADDS (nothing in src/ reads it yet — D-10)                       ║ │
│   ║                                                                            ║ │
│   ║  include/eprom_params.h   ──> eprom_params_t {max_pulses, overprogram_*,   ║ │
│   ║                                verify_mode, vpp_path, energy_cap_us}       ║ │
│   ║  src/proms/eprom_params.cpp ─> EPROM_PARAMS[] PROGMEM  (3 rows)            ║ │
│   ║                                eprom_params_for(protocol) → row | NULL     ║ │
│   ║                                          ▲                                 ║ │
│   ║   140-CITATIONS sidecar (JSON) ──────────┘  one entry per (row, column)    ║ │
│   ║                                                                            ║ │
│   ║   GC'd out of the AVR image (verified: -ffunction-sections/-fdata-sections/║ │
│   ║   -Wl,--gc-sections) ⇒ Phase 140 AVR flash delta ≈ 0                       ║ │
│   ╚════════════════════════════════════════════════════════════════════════════╝ │
│                                    │                                             │
│              eprom.cpp:143 eprom_write_execute()      ◀── UNCHANGED in 140       │
│                 ├─ :145  protocol==0x0B || FLAG_VPE_AS_VPP → VPP route (Ph.142)  │
│                 ├─ :155  mismatch_bitmask[DATA_BUFFER_SIZE/8]  (Ph.141 removes)  │
│                 ├─ :163  for w < NUMBER_OF_RETRIES(20)         (Ph.141 removes)  │
│                 └─ :177  pulse_delay = org + org*retries/20    (Ph.141 removes)  │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘

  PROOF SURFACE (all CI-executed unless marked):
   firmware  pytest tests/ -v ......... 227 pass — where D-13 + D-14 gates belong
   firmware  pio test -e native ....... 141 cases / 17 suites  [PINNED — must not move]
   firmware  pio test -e native_nodevtools 141 / 17            [PINNED — must not move]
   firmware  pio test -e native_trace_v131  5 / 1  [NOT in CI] [D-10 keeps GREEN]
   firmware  pio test -e native_params_v131 NEW    [NOT in CI] [D-11 — run by name]
   app       pytest tests/ ............ 1539 pass — where the DB-half gate belongs
```

### Recommended Project Structure

```
firestarter/                                     # submodule 1 — commits_land_in
├── include/
│   └── eprom_params.h                # NEW: types, enums, extern decl. Includes ONLY
│                                     #      <stdint.h> + rurp_platform_compat.h.
│                                     #      NO Arduino.h, NO rurp_shield.h  (Pitfall 1)
├── src/proms/
│   ├── eprom_params.cpp              # NEW: PROGMEM table + eprom_params_for().
│   │                                 #      Includes ONLY eprom_params.h. (Pitfall 1)
│   └── eprom.cpp                     # BYTE-UNCHANGED (D-10)
├── test/native/avr/
│   └── test_eprom_params_v131/       # NEW suite (D-11's fifth env)
│       ├── host_stubs.cpp            # minimal — see Pitfall 6
│       └── test_eprom_params_v131.cpp
├── tests/                                        # Python gates — CI: pytest tests/ -v
│   ├── test_eprom_params_citations.py    # NEW: D-14 coverage gate
│   ├── test_protocol_branch_inventory.py # NEW: D-13 pinned-inventory gate
│   └── golden/
│       ├── eprom_params_citations.json   # NEW: the TABLE-04 sidecar (D-14)
│       └── protocol_branch_inventory.json# NEW: the D-13 pin
├── platformio.ini                    # + [env:native_params_v131]  (copy of :293-328)
└── doc/PROTOCOLS.md                  # UPDATE if any row value changes (see F-140-09)

firestarter_app/                                 # submodule 2 — commits_land_in
└── tests/
    ├── test_chip_database_field_inventory.py # NEW: D-12's DB half
    └── golden/chip_database_field_inventory.json  # NEW: frozen key set + counts
```

### Pattern 1: PROGMEM const table + fail-closed accessor

**What:** A `static const` struct array in flash, reached by a linear scan over `protocol_id`.
**When to use:** 3 rows, read-rarely, RAM budget exactly 0.
**Why not a switch:** a `switch` returning six values is a second selector by D-13's own definition.

The in-tree precedent (`src/json_parser.c:133`, verbatim):
```c
static const key_parser_t key_parsers[] PROGMEM = {
    {key_mem_size, get_memory_size}, {key_address, get_address}, ...
};
// access:
PGM_P key = (PGM_P)pgm_read_ptr(&key_parsers[j].key);          // json_parser.c:302
```

### Pattern 2: The fifth native env (verbatim shape from `platformio.ini:293-328`)

```ini
[env:native_params_v131]
; FIFTH native environment (Phase 140 / D-11) — TABLE-03's fallback test.
; HARD CONSTRAINT — MUST NEVER be folded into [env:native] or
; [env:native_nodevtools]'s test_filter: both are pinned at exactly 141 cases /
; 17 suites by check_size_baseline.py's compare_native. Names ONLY its own suite.
; NOT in default_envs (:16) — pio run would try to link a main()-less target.
; Do NOT feed "native_params_v131" to check_size_baseline.py (uncaught KeyError,
; exit 1 — F-138-05) nor to check_build_warnings.py (exit 2, no baseline entry).
platform = native
test_framework = unity
test_filter =
	native/avr/test_eprom_params_v131
build_flags =
	${env:native.build_flags}
	-I test/native/avr/test_eprom_params_v131
lib_deps =
	fabiobatsilva/ArduinoFake@^0.4.0
build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>
test_build_src = yes
```
`${env:native.build_flags}` inheritance is the `native_pinmap_provisional` idiom
(`platformio.ini:285`) — it carries `-I include` and every existing suite `-I`, so the new header is
already on the include path.

### Pattern 3: Committed-inventory gate (the recommended D-13/D-14 shape)

`tests/test_golden_trace_identity_eprom_v131.py` is the in-milestone precedent and is the pattern to
copy, not import (its own docstring explains why a shared-helper refactor disarms the self-scan). Its
six-test shape maps 1:1 onto what D-13/D-14 need:

1. blob-SHA identity of the pinned artifact (`git rev-parse HEAD:<path>`)
2. names parsed live from the file == names in the committed JSON
3. per-item counts match positionally, naming the **first** divergence
4. **non-vacuity** — the JSON records ≥ N items and every count ≥ 1
5. the consumer still references the artifact (so it stays load-bearing)
6. **fail-closed self-scan** — the module's own source contains no `pytest.skip` / `@skipif`

### Anti-Patterns to Avoid

- **A `switch (protocol)` inside the accessor.** That is the second selector TABLE-05 forbids —
  the table must be the lookup, the accessor a scan over it.
- **`__attribute__((used))` or a `static_assert` on the table to "prove" it is real.** Explicitly
  rejected by D-10; burns Uno-class headroom on code nothing calls.
- **An app-side gate that reads firmware source.** Failed open 4× in Phase 117; D-12 forbids it;
  `tests/test_dev_gate_reads_no_firmware_source.py` is the app repo's own codification of the lesson.
- **A meta-repo script scanning both working trees.** Runs in no CI leg of either sub-repo — a
  local-run obligation, not a gate (D-12's rejected option).
- **Re-baselining `scripts/baseline/size_baseline.json` to absorb a count change.** Phase 138
  created `size_baseline_v131.json` precisely so nothing moves the live baseline before Phase 144.
- **Citing a datasheet by repo path.** See F-140-08: the paths `doc/PROTOCOLS.md` already uses do not
  resolve on this branch.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Pinning an artifact against silent edits | A hand-written "expected contents" string in the test | `tests/test_golden_trace_identity_eprom_v131.py`'s blob-SHA + independent re-parse + non-vacuity + fail-closed-self-scan shape | Already in-milestone, already CI-green (6 of the firmware repo's 227 passing tests), already survived its own planted-failure discipline |
| Cross-repo path resolution | `os.path.join(_HERE, "..", "firestarter", …)` | Don't cross repos at all (D-12) | `tests/scan_paths.py` documents that 7 of 11 app tools built the "cross-repo" path with a single `..` and silently resolved into the app's **own** package — the same-name collision trap |
| Target resolution in a new checker | `_HERE`-relative defaults copied from a prior phase | Explicit target list + a self-check that every default resolves where expected + a non-zero scanned count in the PASS line | `check_permitted_claims.py`'s `_HERE` resolved to the checker's own phase dir → scanned nothing, exited 0. `139-check-claims.py:151-202, 271, 321` is the corrected re-derivation |
| Re-deriving the pulse distribution | A fresh ad-hoc script | `.planning/phases/138-preconditions-baseline/138-pulse-distribution.py` | Already proved its own capacity to fail (planted Run 1); its figures are frozen in `138-02-PULSE-DISTRIBUTION.md` and re-verified independently this session (§F-140-04) |
| Detecting DB drift | A new full-DB differ | `tools/diff_db.py` GATE-02 for *drift*; a frozen key-inventory pytest for *schema* | `_diff_field_paths` (`diff_db.py:373-392`) already unions both key sets, so it sees a new field — but it is silenceable by regenerating `tools/baseline/chip_database.baseline.json`. The TABLE-05 gate must be the non-silenceable half |
| Host-side PROGMEM emulation | A hand-written `avr/pgmspace.h` in the new suite | `include/rurp_platform_compat.h` (already provides `PROGMEM`, `pgm_read_byte/word/dword/ptr`, `memcpy_P`, `strcpy_P`, …) | Adding another shim is how the 14-warnings-per-TU redefinition storm got started (`size_baseline.json:warnings.note`) |
| A stateful chip read-back model for the fallback test | Re-deriving stubs | `test/native/avr/_shared/host_stubs_common.inc` — but see Pitfall 6: the fallback test needs **none** of the three recorders | `configure_eprom` performs no hardware I/O beyond `mem_util_set_address(handle,0)` |

**Key insight:** every proof mechanism this phase needs already exists in-tree, authored within the
last two milestones, with its own failure modes documented. The work is composition and attribution,
not invention.

---

## Datasheet Attribution Matrix

Eight primary datasheets were read in full this session. Provenance and machine-readability differ
and matter (see F-140-08).

| Datasheet | Where it came from | Text layer? |
|---|---|---|
| Winbond **W27C512**, Rev A4, pub. Nov 1999 | `firestarter_app/datasheets/W27C512.pdf` — **untracked working-tree file** | yes |
| ST **M27C512**, Rev 3, May 2007 | `firestarter_app/datasheets/M27C512.pdf` — **untracked** (same doc as Farnell 1581208) | yes |
| Microchip **27C512A**, DS11173G, 2004 | fetched from `ww1.microchip.com/downloads/en/DeviceDoc/11173G.pdf` | yes |
| AMD **Am27C020** (FINAL) | `git show v1.16-protocol-first-architecture-rebuild:datasheets/0x08-EPROM-QUICK/AM27C020.pdf` | yes |
| ST **M27C1001** (27C010-class) | `firestarter_app/datasheets/M27C1001.pdf` — **untracked** | yes |
| Winbond **W27C020** (Preliminary) | `firestarter_app/datasheets/W27C020.pdf` — **tracked** | yes |
| Intel **27C010** | fetched from `ardent-tool.com/datasheets/Intel_27C010.pdf` | **no** — rendered to PNG and read |
| TI **TMS 2516-25/35/45 JL**, Dec 1979 rev. May 1982 | `git show v1.16-…:datasheets/0x0B-EPROM-LEGACY/2516_EPROM.pdf` | **no** — scanned; rendered to PNG and read |

### Verbatim findings

**Winbond W27C512, "SMART PROGRAMMING ALGORITHM 2"** `[VERIFIED: PDF read in-session]`
`X=0` → Program one 100 µS Pulse (OE/VPP = 12 V) → Increment X → **`X = 25?`** → Yes ⇒ Device Failed;
No ⇒ Verify One Byte (OE/VPP = VIL, Vcc = 5.0 V) → Pass ⇒ next address. After the last address:
**"Compare All Bytes to Original Data"**. No overprogram step in either of its two algorithms.
AC table: `TPWP` CE Program Pulse Width = 95 / **100** / 105 µs; VPP 11.75 / 12.0 / 12.25 V; VCC
during program (VCP) 4.75 / **5.0** / 5.25 V.

**ST M27C512 §2.6 "PRESTO IIB programming algorithm"** `[VERIFIED]`
> "…a sequence of 100µs program pulses are applied to each byte until a correct verify occurs.
> **No overprogram pulses are applied** since the verify in MARGIN MODE provides the necessary margin."

Fig. 4 flowchart: `VCC = 6.25V, VPP = 12.75V` → SET MARGIN MODE → `n=0` → `E = 100µs Pulse` →
`++n = 25` ⇒ FAIL → else VERIFY → last addr → RESET MARGIN MODE → **CHECK ALL BYTES: 1st VCC = 6V,
2nd VCC = 4.2V**.

**Microchip 27C512A §1.6 "Programming Mode"** `[VERIFIED]`
> "The **Express** algorithm must be used for best results… **Up to 10 100-microsecond pulses are
> applied until the byte is verified.**"

Fig. 1-3: `X = 10?` ⇒ Device Failed. Final pass: `VCC = VPP = 4.5V, 5.5V` → "All bytes = original
data?". Note 3 to the AC table: `VCC = 6.5V ±0.25V, VPP = VH = 13.0V ±0.5V for express programming`.

**AMD Am27C020, "Programming the Am27C020"** `[VERIFIED]`
> "The **Flashrite** algorithm reduces programming time by using **100 µs programming pulse** and by
> giving each address only as many pulses as are necessary… After each pulse is applied to a given
> address, the data in that address is verified. If the data does not verify, additional pulses are
> given **until it verifies or the maximum is reached**… This part of the algorithm is done at
> **VCC = 6.25 V**… After the final address is completed, **the entire EPROM memory is verified at
> VCC = VPP = 5.25 V**."

No overprogram step. **The numeric maximum is not stated in this document** — "the maximum" is
unquantified.

**ST M27C1001 §2.6 "Presto II programming algorithm"** `[VERIFIED]`
> "…applying a sequence of 100µs program pulses to each byte until a correct verify occurs…
> **No overprogram pulse is applied** since the verify in Margin mode provides necessary margin to
> each programmed cell."

Fig. 5: `VCC = 6.25V, VPP = 12.75V`, `n=0`, `P = 100µs Pulse`, `++n = 25` ⇒ FAIL, then
**CHECK ALL BYTES: 1st VCC = 6V, 2nd VCC = 4.2V**.

**Winbond W27C020, "SMART PROGRAMMING ALGORITHM"** `[VERIFIED]`
`Vcc = 5V, Vpp = 12V`; `X=0`; Program One 100 µS Pulse; Increment X; **`X = 25?`** ⇒ Fail Device;
else Verify One Byte; after last address `Vcc = 5V, Vpp = 5V` → **"Compare All Bytes to Original
Data"**. No overprogram step. AC: `TPWP` = 95 / **100** / 105 µs.

**Intel 27C010** `[VERIFIED: pages rendered and read]`
DC/AC Programming: `tPW` PGM Program Pulse Width = 95 / **100** / 105 µs; `VPP` 12.5 / **12.75** /
13.0 V; `VCP` (VCC during program) 6.0 / **6.25** / 6.5 V. "Program Verify… **With VCC at 6.25 V, a
substantial program margin is ensured.**" No pulse-count flowchart appears in this document.

**TI TMS 2516, "start programming" (p.138) + AC table (p.141) + "program verification" (p.139)**
`[VERIFIED: scanned pages rendered and read]`
> "Once addresses and data are stable, a **50-millisecond TTL high-level pulse should be applied to
> the PGM pin at each address location to be programmed. Maximum pulse width is 55 milliseconds.**
> Locations can be programmed in any order."

AC "recommended timing requirements for programming": **`t_w(PR)` Pulse width, program pulse =
MIN 45 / TYP 50 / MAX 55 ms**; Vpp = 25 V ± 1 V during programming.
Mode table: Start Programming — PD/PGM pulsed VIL→VIH, CS = VIH, **VPP = +25 V**, VCC = +5 V.
Program Verification — PD/PGM = VIL, CS = VIL, **VPP = +25 V (or +5 V)**, VCC = +5 V.
> "A verification… **can be done on each location immediately after that location is programmed. To
> do a verification, Vpp may be kept at +25 V.**"

Front page: "…requiring a single 50-ms pulse… **Total programming time for all bits is 100 seconds.**"

### Per-cell verdicts

| Row | Column | Value | Basis | Verdict |
|---|---|---|---|---|
| `0x07` | `max_pulses` | **25** | Winbond W27C512 Rev A4 SMART ALG 2 `X = 25?`; ST M27C512 Rev 3 Fig. 4 `++n = 25` | **DATASHEET** — with the mandatory scope note that Microchip 27C512A DS11173G §1.6 specifies **10**; 25 is the maximum across the row's cited datasheets, chosen so no compliant part is refused |
| `0x07` | `overprogram_factor` | 3 (locked by `PROJECT.md`'s throughput table + D-08's "both overprogramming rows") | **None of the three 0x07 datasheets read supports it** — all three explicitly apply no overprogram. Supported only for the Intel-family 1 ms sub-population (22 of 170 chips, §F-140-05) | **⚠ SPLIT — see F-140-05 and Open Question 1.** Attribution available: "Intel Intelligent Programming family (1 ms pulse × N, then 3 × N overprogram)"; the 3× formula itself is `[ASSUMED]` — no Intel Intelligent datasheet with a readable flowchart was obtainable this session |
| `0x07` | `overprogram_cap_us` | 75000 | `3 × 25 × 1000 µs`; the figure publicly stated on gh#15 | **REASONED** — "no datasheet basis — reasoned from: Intel Intelligent worst case at the row's largest DB pulse (1000 µs) × the datasheet max-pulse count (25); also the figure published in the gh#15 correction" |
| `0x07` | `verify_mode` | `VERIFY_PER_PULSE_PLUS_FINAL` | W27C512 "Compare All Bytes to Original Data"; M27C512 "CHECK ALL BYTES"; 27C512A "All bytes = original data?" | **DATASHEET** — plus the D-02 mandatory clause: the final pass's specified VCC levels (6 V/4.2 V ST; 4.5 V/5.5 V Microchip) are **unreachable on the RURP**; this column encodes *when*, never *at what VCC* |
| `0x07` | `vpp_path` | drop-resistor | ST M27C512 VPP 12.75 V ± 0.25; Winbond W27C512 VPP 11.75/12.0/12.25 V; matches `eprom.cpp:150` `CTRL_VPP_REGULATOR_ENABLE \| CTRL_VPP_VPE_DROP_ENABLE` | **DATASHEET** (voltage target) + **CODE** (route) |
| `0x07` | `energy_cap_us` | 0 (uncapped) | — | **REASONED** — "no datasheet basis — reasoned from: no 28-pin datasheet read specifies a per-byte energy budget; 0 = the sentinel for 'no cap'" |
| `0x08` | `max_pulses` | **25** | Winbond W27C020 `X = 25?`; ST M27C1001 Fig. 5 `++n = 25` | **DATASHEET** — with the note that the D-09 representative part (AMD Am27C020) says "until it verifies or the maximum is reached" **without a number** |
| `0x08` | `overprogram_factor` | **0** | ST M27C1001 §2.6 verbatim "No overprogram pulse is applied"; AMD Am27C020 Flashrite description contains no overprogram step; Winbond W27C020 flowchart has none | **DATASHEET — D-06 RESOLVED.** Three independent vendors, including the 27C010-class part D-06 names by name. Agrees with `PROJECT.md`'s prose; **contradicts `PROJECT.md`'s own throughput table**, which must be named explicitly in the phase record |
| `0x08` | `overprogram_cap_us` | 75000 | inert on this row once the factor is 0 | **REASONED** — "no datasheet basis — reasoned from: uniform ceiling with `0x07`; inert on this row because `overprogram_factor = 0`". ⚠ D-08's phrase "both overprogramming rows" presupposed two rows; research finds one |
| `0x08` | `verify_mode` | `VERIFY_PER_PULSE_PLUS_FINAL` | AMD "the entire EPROM memory is verified at VCC = VPP = 5.25 V"; Winbond "Compare All Bytes"; ST "CHECK ALL BYTES" | **DATASHEET** + the same 6.25 V-ceiling clause (AMD programs at 6.25 V, verifies at 5.25 V; neither is reachable) |
| `0x08` | `vpp_path` | drop-resistor (+ P1 routing for DIP32) | Intel 27C010 VPP 12.75 V; AMD Am27C020 VPP 12.75 V ± 0.25; W27C020 Vpp 12 V | **DATASHEET** (voltage) + **CODE** (`eprom.cpp:150`; `using_p1_as_vpp` at `:320`) |
| `0x08` | `energy_cap_us` | 0 (uncapped) | — | **REASONED** — same wording as `0x07` |
| `0x0B` | `max_pulses` | backstop — **recommend 255** | — | **REASONED** — "no datasheet basis — reasoned from: termination bound". §F-140-06 derives the floor: it must be ≥ **250** or it pre-empts the energy cap on the 200 µs sub-population (5 of 32 chips). 255 is the smallest `uint8_t`-representable value ≥ 250 |
| `0x0B` | `energy_cap_us` | **50000** | TI TMS 2516 `t_w(PR)` = 45 / **50** / 55 ms; "a 50-millisecond TTL high-level pulse should be applied… at each address location"; "Maximum pulse width is 55 milliseconds" | **DATASHEET — stronger than the milestone record assumed.** ⚠ See F-140-07: the *justification sentence* published on gh#15 ("100 × 500 µs is the classic 2716 **total programming time**") is wrong — the datasheet's total for all bits is **100 seconds**. The value is correct; the reason is not |
| `0x0B` | `verify_mode` | `VERIFY_PER_PULSE` | TMS 2516 p.139: verification "can be done on each location immediately after that location is programmed"; no final full-array pass is specified anywhere in the document | **DATASHEET** |
| `0x0B` | `vpp_path` | direct VPE (no drop) | TMS 2516 mode table: Start Programming VPP = **+25 V**; Program Verification VPP = +25 V (or +5 V) — corroborating both the direct rail and VPE-held-across-verify | **DATASHEET** + **CODE** (`eprom.cpp:147`) |
| `0x0B` | `overprogram_factor` | 0 | TMS 2516 specifies a single pulse per location, no overprogram | **DATASHEET** |
| `0x0B` | `overprogram_cap_us` | 75000 (uniform) or 0 | inert — factor is 0 | **REASONED** — same wording as `0x08` |

---

## Common Pitfalls

### Pitfall 1 — A new `src/proms/*.cpp` in the house include style turns a live gate RED
**What goes wrong:** `check_build_warnings.py` fails on `native` / `native_nodevtools`.
**Why it happens:** measured cold this session — `pio test -e native_trace_v131` after
`rm -rf .pio/build/native_trace_v131` emits **140 warnings, all macro redefinitions, exactly 14 per
translation unit** across 10 TUs:

```
    14  test/native/avr/test_trace_eprom_v131/host_stubs.cpp
    14  src/proms/memory.cpp        14  src/proms/flash_utils.cpp
    14  src/proms/flash_nor_unlock.cpp  14  src/proms/flash_intel.cpp
    14  src/proms/flash_5v_page.cpp     14  src/proms/eprom.cpp
    14  src/proms/eeprom_28c.cpp        14  src/operation_utils.cpp
    14  src/boards/rurp_serial_utils.cpp
```
The redefinitions are ArduinoFake's `arduino/pgmspace.h` vs `test/native/avr/test_dispatch/avr/pgmspace.h`
(`PSTR`, `memcpy_P`, `strcpy_P`, …). The live watermark is `native: total_watermark 1166`,
`native_nodevtools: 1166`, policy `<= total_watermark`, and Phase 138 recorded both as
"matches exactly, **no headroom**". `build_src_filter = +<proms/>` is identical in all five native
envs, so the new file lands in the pinned pair too.
**How to avoid:** `src/proms/not_implemented.cpp` includes `firestarter.h` but **not** `<Arduino.h>`
and emits **zero** of these warnings (verified — it is absent from the 10-TU list above). Keep the new
`.cpp` free of `<Arduino.h>`; a table of integers needs nothing from it. Cleanest: the `.cpp` includes
only `eprom_params.h`, which includes only `<stdint.h>` and `rurp_platform_compat.h`.
**Warning signs:** any `#include <Arduino.h>` in the new files; a cold `native` warning count ≠ 1166.
**Measurement discipline:** warm builds under-count badly (`size_baseline.json:warnings.note` records
warm native = 998 vs cold 1166). Any warning check must `rm -rf .pio/build/<env>` first and use a
**single** uninterrupted invocation.

### Pitfall 2 — `sizeof(eprom_params_t)` differs between AVR and the native test
**What goes wrong:** a native test asserting the struct's size fails, or the PROGMEM budget is
mis-predicted.
**Why it happens:** avr-gcc gives every type 1-byte alignment; x86-64 does not. Declared as
`{uint8_t, uint8_t, uint32_t, uint8_t, uint8_t, uint32_t}` the struct is **12 B on AVR** and
**16 B on x86-64** (two 2-byte pads).
**How to avoid:** order fields largest-first — `uint32_t overprogram_cap_us; uint32_t energy_cap_us;
uint8_t max_pulses; uint8_t overprogram_factor; uint8_t verify_mode; uint8_t vpp_path;` → **12 B on
both**. Budget: 3 rows × 12 B = **36 B PROGMEM** plus the accessor. Against the fork-base MERGE-05
headroom (42 B `uno` / 36 B `uno328pb`) that is already tight, and against the live `beta` tip
(F-138-02: 8 B / 2 B) it does not fit — but Phase 140's own delta is ≈ 0 because the table is
garbage-collected (Pitfall 3). Phase 141 pays for it, funded by LOOP-02's removals.

### Pitfall 3 — Assuming the table will show up in Phase 140's flash delta
**What goes wrong:** a ~0 delta is read as "we forgot to add the table".
**Why it happens:** verified this session — `~/.platformio/platforms/atmelavr/builder/frameworks/arduino.py`
lines 98-99 and 111 pass `-ffunction-sections`, `-fdata-sections` and `-Wl,--gc-sections`. Nothing in
`src/` references the table (D-10), so both the array and the accessor are collected.
**How to avoid:** state the ≈0 prediction in the phase record **before** measuring, exactly as
CONTEXT `<specifics>` requires, so Phase 144 / TEST-08 reconciles a prediction rather than reporting a
surprise.

### Pitfall 4 — `handle->pulse_delay` is not reset between commands
**What goes wrong:** a test (or a real session) believes it is exercising the `pulse_delay == 0`
fallback and is not.
**Why it happens:** `firestarter_handle_t handle;` is a file-scope global (`src/firestarter.cpp:32`),
and `json_parse` (`src/json_parser.c:164-278`) resets `address`, `ctrl_flags`, four `bus_config` fields
and `chip_id` — **not** `pulse_delay`, `protocol`, `mem_size`, `vpp_mv` or `pins`. Compounding it,
`eprom_write_execute` restores `org_delay` on the success path (`eprom.cpp:172`) but **not** on the
retry-exhausted failure path (`:181-192`), so an inflated value can survive into the next command.
**How to avoid:** the TABLE-03 test must construct a fresh zero-initialised handle per case
(`firestarter_handle_t h = {};`, the `test_trace_eprom_v131.cpp:217` idiom) and must include a
**negative control** (`pulse_delay = 777` stays 777) so the assertion cannot pass vacuously.
**Warning signs:** a fallback test that passes without a negative control.

### Pitfall 5 — D-13's gate is RED on arrival on two pre-existing branches
**What goes wrong:** the gate can never be seen to pass, so D-15's "fix the locator, not the
assertion" trap fires.
**Why it happens:** the complete measured inventory of branches in the EPROM path is:

| Site | Keyed on | Class |
|---|---|---|
| `eprom.cpp:71` `switch (handle->protocol)` | `protocol` | algorithm selector (stays — D-03) |
| `eprom.cpp:145` `protocol == 0x0B \|\| is_flag_set(FLAG_VPE_AS_VPP)` | `protocol` **and `ctrl_flags`** | VPP route (Phase 142) |
| `eprom.cpp:218` same predicate | `protocol` **and `ctrl_flags`** | VPP route (Phase 142) |
| `eprom.cpp:320` `using_p1_as_vpp(handle)` | **`pins` + `bus_config.vpp_line`** (`memory_utils.h:24-28`) | pin routing — pre-existing |

D-13's rule "a branch keyed on **any other** handle field fails the gate" hits the last three.
**How to avoid:** the pinned inventory must carry a reasoned allowlist distinguishing *algorithm
selection* from *hardware routing*, naming `FLAG_VPE_AS_VPP` (`:145`, `:218`) and `using_p1_as_vpp`
(`:320`) as pre-existing routing predicates. Also note `:145` and `:218` spell the protocol as raw
`0x0B` — `eprom.cpp` does **not** include `proto_constants.h` — so a locator matching only
`PROTO_EPROM_24PIN` finds nothing, and one matching only `0x0B` breaks when Phase 142 adopts the token.

### Pitfall 6 — Over-building the fallback suite's host stubs
**What goes wrong:** wasted work, and needless coupling to the three opt-in recorder layers.
**Why it happens:** `test_trace_eprom_v131` needs `HOST_STUBS_REAL_REGISTER_UTILS` +
`HOST_STUBS_RECORD_TIMING` + `HOST_STUBS_CUSTOM_READ_DATA_BUFFER` because it traces hardware cadence.
The TABLE-03 test does not: `configure_eprom` performs no hardware I/O, and `configure_memory`'s only
bus touch is `mem_util_set_address(handle, 0)` (`memory.cpp:93`) — which `test_val_eprom`'s negative
controls already prove sets no VPP bit.
**How to avoid:** the new suite's `host_stubs.cpp` should be the plain `#include "../_shared/host_stubs_common.inc"`
with **no** opt-in guards. `delay()` still needs a fakeit stub in `setUp()` if the test reaches
`eprom_check_vpp` — it does not, if the test calls `configure_memory`/`configure_eprom` only and never
`firestarter_operation_init`.

### Pitfall 7 — The `native_params_v131` env is invisible to both live gates
**What goes wrong:** a green CI run is mistaken for coverage of the new suite.
**Why it happens:** F-138-05 — `check_size_baseline.py` hardcodes
`NATIVE_ENVS = ("native", "native_nodevtools")` (`scripts/check_size_baseline.py:100`) and
`compare_native` does a bare dict lookup ⇒ uncaught `KeyError`, exit 1. `check_build_warnings.py`
handles it cleanly (exit 2) but has no baseline entry. **Neither firmware CI workflow runs
`native_pinmap_provisional` or `native_trace_v131` at all** — `build.yml:142,155` and
`beta-build.yml:122,128` run only `native` and `native_nodevtools`.
**How to avoid:** run `pio test -e native_params_v131` **explicitly by name** in this phase's own
verification and record its case/suite counts in the phase record, exactly as D-11 requires. Do not
add the env name to either gate's arguments.

### Pitfall 8 — A `scripts/check_*.py` drags in five extra obligations
**What goes wrong:** `tests/test_checker_convention.py` goes RED.
**Why it happens:** it globs `scripts/check_*.py` non-recursively and asserts, for each: a paired
`tests/test_check_<X>.py`; ≥1 `tests/fixtures/planted_<X>*`; the checker's exact filename inside the
test module; a `returncode != 0` assertion in it; plus hardcoded `FLOOR = 6` and `FIXTURE_FLOOR = 15`
that "a later phase that adds a firmware checker raises deliberately in the SAME commit".
Current counts verified: 6 checkers, 15 planted fixtures — both exactly at their floors.
**How to avoid:** prefer the standalone-pytest gate shape (Pattern 3), which is outside the glob. If
an executable checker really is wanted, budget all five obligations into the same plan.

---

## Code Examples

### The header — dependency-free, both-platform-stable layout

```c
/* include/eprom_params.h — Phase 140 (TABLE-01/02).
 * Deliberately includes NOTHING from Arduino or rurp_shield: see 140-RESEARCH
 * Pitfall 1 (a TU that pulls in both <Arduino.h> and the avr/pgmspace.h shim
 * emits 14 macro-redefinition warnings, and check_build_warnings.py's native
 * watermark of 1166 has zero headroom).
 * Field order is largest-first so sizeof() == 12 on AVR *and* on x86-64
 * (avr-gcc has 1-byte alignment for everything; the host does not).
 * NO PULSE-WIDTH COLUMN — TABLE-02. Pulse width is handle->pulse_delay; the
 * per-protocol fallback constants stay in configure_eprom (eprom.cpp:71-76, D-03).
 */
#ifndef __EPROM_PARAMS_H__
#define __EPROM_PARAMS_H__

#include <stdint.h>
#include "rurp_platform_compat.h"   /* PROGMEM + pgm_read_* on AVR and host alike */

enum { VERIFY_PER_PULSE = 0, VERIFY_PER_PULSE_PLUS_FINAL = 1 };
/* Abstract, NOT control-register masks — Phase 142 owns the mask sets. */
enum { VPP_PATH_DROP_RESISTOR = 0, VPP_PATH_DIRECT_VPE = 1 };

typedef struct {
    uint32_t overprogram_cap_us;   /* clamp for min(3*N*pulse, cap) — D-08     */
    uint32_t energy_cap_us;        /* 0 = uncapped — D-01                      */
    uint8_t  max_pulses;
    uint8_t  overprogram_factor;   /* 0 or 3 — D-06                            */
    uint8_t  verify_mode;
    uint8_t  vpp_path;
} eprom_params_t;                  /* 12 bytes on AVR and on x86-64            */

#ifdef __cplusplus
extern "C" {
#endif
/* Returns a POINTER INTO PROGMEM (read fields with pgm_read_*), or NULL when
 * no row matches — the caller fails closed with zero hardware side effects (D-05). */
const eprom_params_t* eprom_params_for(uint32_t protocol);
#ifdef __cplusplus
}
#endif
#endif  /* __EPROM_PARAMS_H__ */
```

### The table TU — no `<Arduino.h>`, PROGMEM, linear scan (no second selector)

```c
/* src/proms/eprom_params.cpp — Phase 140.
 * Storage precedent: static const key_parser_t key_parsers[] PROGMEM
 * (src/json_parser.c:164), including the pgm_read_* access idiom (:114).
 * MUST NOT #include <Arduino.h> — see 140-RESEARCH Pitfall 1.
 * Every value's citation: tests/golden/eprom_params_citations.json (D-14).
 */
#include "eprom_params.h"

/* protocol_id is the sole key (TABLE-05). A switch here would be a second
 * selector; the table IS the lookup and this is a scan over it. */
static const uint8_t  EPROM_PARAM_KEYS[] PROGMEM = { 0x07, 0x08, 0x0B };
static const eprom_params_t EPROM_PARAMS[] PROGMEM = {
    /* 0x07 PROTO_EPROM_28PIN */ { 75000UL, 0UL,     25, 3, VERIFY_PER_PULSE_PLUS_FINAL, VPP_PATH_DROP_RESISTOR },
    /* 0x08 PROTO_EPROM_32PIN */ { 75000UL, 0UL,     25, 0, VERIFY_PER_PULSE_PLUS_FINAL, VPP_PATH_DROP_RESISTOR },
    /* 0x0B PROTO_EPROM_24PIN */ { 75000UL, 50000UL, 255, 0, VERIFY_PER_PULSE,           VPP_PATH_DIRECT_VPE    },
};

const eprom_params_t* eprom_params_for(uint32_t protocol) {
    for (uint8_t i = 0; i < (uint8_t)(sizeof(EPROM_PARAM_KEYS) / sizeof(EPROM_PARAM_KEYS[0])); i++) {
        if ((uint32_t)pgm_read_byte(&EPROM_PARAM_KEYS[i]) == protocol) {
            return &EPROM_PARAMS[i];
        }
    }
    return NULL;   /* D-05: fail closed, zero hardware side effects */
}
```
*(Row values above are the research-recommended set; `0x0B`'s `max_pulses` is the F-140-06 floor.)*

> **SUPERSEDED — `0x07` ships `overprogram_factor = 0`, not the `3` in the block above (nor the
> "0 or 3" in the header comment).** Open Question 1 was resolved on 2026-08-09 by operator decision
> during `/gsd-plan-phase 140`; the binding values are `140-01-PLAN.md`'s `<locked_values>` table,
> which that plan instructs the executor to use *instead of* copying this example's row block. Do
> not copy the `/* 0x07 PROTO_EPROM_28PIN */` line verbatim.

### The TABLE-03 fallback test — exercised, not asserted, with a negative control

```cpp
/* test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp */
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>
extern "C" { #include "memory.h" }
#include "firestarter.h"
#include "eprom_params.h"
using namespace fakeit;

void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
    When(Method(ArduinoFake(), delay)).AlwaysReturn();   /* mem_util path safety */
}
void tearDown(void) {}

/* Fresh handle per case — the global handle never resets pulse_delay
 * (json_parser.c:164-278; 140-RESEARCH Pitfall 4). */
static firestarter_handle_t mk(uint32_t proto, uint32_t pulse) {
    firestarter_handle_t h = {};
    h.protocol = proto; h.cmd = CMD_WRITE; h.response_code = RESPONSE_CODE_OK;
    h.mem_size = 2048; h.ctrl_flags = FLAG_SKIP_BLANK_CHECK | FLAG_SKIP_ERASE;
    h.pulse_delay = pulse;
    return h;
}

static void assert_fallback(uint32_t proto, uint32_t expected, const char* ctx) {
    firestarter_handle_t h = mk(proto, 0);       /* EXERCISE the zero path */
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code, ctx);
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(expected, h.pulse_delay, ctx);
}

static void assert_no_override(uint32_t proto, const char* ctx) {
    firestarter_handle_t h = mk(proto, 777);     /* NEGATIVE CONTROL */
    configure_memory(&h);
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(777UL, h.pulse_delay, ctx);
}

void test_0x07_zero_pulse_delay_takes_the_1000us_fallback(void) { assert_fallback(0x07, 1000UL, "0x07"); }
void test_0x08_zero_pulse_delay_takes_the_100us_fallback(void)  { assert_fallback(0x08,  100UL, "0x08"); }
void test_0x0B_zero_pulse_delay_takes_the_500us_fallback(void)  { assert_fallback(0x0B,  500UL, "0x0B"); }
void test_0x07_nonzero_pulse_delay_is_left_alone(void)          { assert_no_override(0x07, "0x07 neg"); }
void test_0x08_nonzero_pulse_delay_is_left_alone(void)          { assert_no_override(0x08, "0x08 neg"); }
void test_0x0B_nonzero_pulse_delay_is_left_alone(void)          { assert_no_override(0x0B, "0x0B neg"); }

/* TABLE-01/05 row resolution — NOTE: this proves TEST-01's content but TEST-01
 * is assigned to Phase 144; do not mark it Complete here. */
void test_each_protocol_resolves_to_its_own_row(void) { /* … distinct non-NULL rows … */ }
void test_unknown_protocol_returns_null(void)         { TEST_ASSERT_NULL(eprom_params_for(0x0C)); }
```

### Recovering the archived datasheet corpus (it is not on this branch)

```bash
# The 21-file datasheets/ tree exists ONLY on v1.16-protocol-first-architecture-rebuild;
# doc/PROTOCOLS.md cites paths under it that do not resolve on the milestone branch.
git -C firestarter show \
  v1.16-protocol-first-architecture-rebuild:datasheets/0x08-EPROM-QUICK/AM27C020.pdf > AM27C020.pdf
git -C firestarter show \
  v1.16-protocol-first-architecture-rebuild:datasheets/0x0B-EPROM-LEGACY/2516_EPROM.pdf > 2516.pdf
# 2516_EPROM.pdf has NO text layer (Acrobat 5.0 Scan Plug-in, zero embedded fonts):
pdftoppm -png -r 170 2516.pdf page      # render, then read the images
```

---

## State of the Art

| Old belief (carried in prior findings / docs) | Current state (measured this session) | Impact |
|---|---|---|
| "Native trace stubs record NO time — `delay()` unstubbed" | **Superseded.** Phase 138 added `HOST_STUBS_RECORD_TIMING` (`host_stubs_common.inc:86-197`) and the suite hooks `delay`/`delayMicroseconds` via fakeit `.AlwaysDo` in its own `setUp()` (`test_trace_eprom_v131.cpp:86-91`). Timing IS captured, interleaved with strobes by a sequence key. | Timing-sensitive assertions are natively possible now |
| "Trace stub caps are 256/512" | Both caps are **512** (`HOST_STUBS_MAX_STROBES` / `HOST_STUBS_MAX_TIMINGS`), with explicit overflow flags | Fine for the small synthetic blocks in use |
| "The v1.16 `primitives.{h,cpp}` layer may exist" | **Confirmed absent.** `find src include -type f` shows no `primitives.*`; the P89 recompose was never merged. There is no primitives seam to build on | The table is a genuinely new TU, not an extension |
| `doc/PROTOCOLS.md` §1.3: "0x07 write algorithm: JEDEC Intelligent Programming (1 ms pulse × N + 3× overpulse)… Citation: `datasheets/0x07-EPROM-STD/W27C512.pdf` p.7 §6.2" | The cited W27C512 datasheet describes **SMART PROGRAMMING** with 100 µs pulses, `X = 25`, and **no overpulse**; there is no §6.2 "Programming Algorithm" in it. §1.4 likewise calls 0x08 "Same Intelligent Programming algorithm" while citing `AM27C020.pdf §Quick-Pulse Programming` | **`doc/PROTOCOLS.md` is a third contradicting document.** If a row value changes, the Algorithm Handlers table in `firestarter/CLAUDE.md` (which says 0x07 = "1ms pulse, DQ7 verify") also needs updating — CONTEXT already flags CLAUDE.md; PROTOCOLS.md is the one it does not |
| The `datasheets/` corpus is available for citation by path | Present **only** on branch `v1.16-protocol-first-architecture-rebuild` (21 files); `git ls-files \| grep -c datasheet` on the milestone branch = **0** | TABLE-04 citations must be self-describing (vendor, part, doc number, revision, date, §/figure), not repo paths |

**Deprecated / outdated:**
- `firestarter/CLAUDE.md` Algorithm Handlers: `0x07` "1ms pulse, DQ7 verify" (DQ7 polling is a
  flash-family mechanism, not a 27C one) and `0x0B` "12–18V direct" (the 2516/2732 NMOS parts are
  25 V; the DB carries `vpp` values up to 25 V on this row).

---

## Findings

**F-140-01 — 14 macro-redefinition warnings per `<Arduino.h>`-including TU; zero headroom.**
Measured cold. See Pitfall 1. Owner: this phase (file layout). `[VERIFIED: measured in-session]`

**F-140-02 — AVR link uses `-ffunction-sections -fdata-sections -Wl,--gc-sections`.**
`~/.platformio/platforms/atmelavr/builder/frameworks/arduino.py:98,99,111`. Confirms D-10's ≈0-delta
prediction mechanically. `[VERIFIED]`

**F-140-03 — `native_trace_v131` is GREEN at HEAD: 5 cases / 1 suite, 2.51 s.**
Re-run this session at firmware `fb7949c`. D-10's "keep it green" premise holds today. `[VERIFIED]`

**F-140-04 — The `pulse_delay == 0` fallback is UNREACHABLE through the shipped database.**
Re-derived independently through the production parser
(`firestarter.database._parse_pulse_duration`): `0x07` n=170 (100×113, 200×27, 1000×22, 500×4, 50×4);
`0x08` n=127 (100×104, 50×11, 10×7, 200×2, 1000×2, 20×1); `0x0B` n=32 (500×21, 1000×6, 200×5) —
byte-for-byte the figures in `138-02-PULSE-DISTRIBUTION.md` and gh#15's C2. **Zero** of the 329 chips
yields 0. The string that does parse to 0, `"Algorithm Controlled"`, appears 417 times DB-wide but on
**no** 27C protocol (it carries protocols 5, 6, 13, 14, 16, 39, 40, 41, 52). The wire field is emitted
unconditionally (`database.py:555`), so a 0 does reach `handle->pulse_delay`. **Consequence: the
native test is the only possible oracle for TABLE-03 — no bench run can reach this path.**
`[VERIFIED]`

**F-140-05 — `0x07` genuinely spans two algorithm families; a single `overprogram_factor` cannot be
right for both.** The 22 chips at 1000 µs on `0x07` are precisely the Intel-family parts: Intel 2764,
2764A, 27128, 27128A, 27512; NEC UPD2764, UPD27C256A; ST/SGS M2764A, M27C64A, ST2764A, ST27C256,
TS27C64A; TI TMS2764; Philips 27C256, 27C512; Toshiba TC54256. The 113 chips at 100 µs are the
PRESTO/SMART/Express generation whose datasheets explicitly apply **no** overprogram. `0x08` is not
similarly split — only 2 of 127 sit at 1000 µs (Philips 27C010, 27C040). **This is the family-split
finding CONTEXT D-06 anticipated, on the row it did not name.** Recommendation: record it for Phase
146 exactly as D-06 directs for `0x08`; do not force a second row (that would be a second dispatch
key). `[VERIFIED: DB query + 6 primary datasheets]`

**F-140-06 — `0x0B`'s `max_pulses` backstop must be ≥ 250, not 100.** To reach the 50 ms energy cap,
the row's three DB pulse values need 250 (@200 µs, 5 chips), 100 (@500 µs, 21 chips) and 50
(@1000 µs, 6 chips) pulses. A backstop below 250 pre-empts the energy cap on the 200 µs
sub-population — silently under-programming 5 chips, which is precisely the failure mode D-07's
"count-only" option was rejected for. **255** is the smallest `uint8_t`-representable value that
clears the floor. `[VERIFIED: arithmetic over the measured distribution]`

**F-140-07 — The `energy_cap_us` justification published on gh#15 is factually wrong; the value is
right.** `PROJECT.md` and the frozen gh#15 comment both say 50 ms "is exactly the classic 2716 total
programming time" derived as `100 × 500 µs`. TI's TMS 2516 datasheet states the **per-location**
program pulse is 50 ms (`t_w(PR)` 45/50/55 ms) and that "**Total programming time for all bits is
100 seconds**". So 50 ms is the datasheet's *single-pulse* figure, not a total, and the value has a
**primary datasheet basis** the milestone believed it lacked. The same datasheet also answers D-02's
"one-shot vs looped" question that was declared unanswerable from source: the classic algorithm is
**one** 50 ms pulse per location, max 55 ms. **This touches published text** — Phase 146 / CLOSE-04
must reconcile it, and the planner should surface it to the operator rather than quietly re-word a
posted claim. `[VERIFIED: scanned datasheet pages read]`

**F-140-08 — No committed datasheet corpus resolves on this branch.** `firestarter/doc/PROTOCOLS.md`
cites `datasheets/<slug>/<file>.pdf` paths; that tree exists only on
`v1.16-protocol-first-architecture-rebuild`. In `firestarter_app/datasheets/`, `W27C020.pdf`,
`AT28C256.pdf` and `SST39SF0x0A.pdf` are tracked, while `W27C512.pdf` (the **bench-required** 0x07
part), `M27C512.pdf`, `M27C1001.pdf` and `W27E257.pdf` are **untracked working-tree files**.
TABLE-04 citations must therefore be self-describing, or the phase must commit the PDFs.
`[VERIFIED: git ls-files / git ls-tree]`

**F-140-09 — `doc/PROTOCOLS.md` contradicts the datasheets it cites.** See §State of the Art. It is a
third document in the D-06 contradiction and is not currently in CONTEXT's update list.
`[VERIFIED]`

**F-140-10 — `tools/diff_db.py` GATE-02 already detects a new `chip_database.json` field.**
`_diff_field_paths` (`diff_db.py:373-392`) unions both key sets, so an added key surfaces as an
unexplained differing path. It is corroboration, not the TABLE-05 gate: it compares against
`tools/baseline/chip_database.baseline.json`, which regenerating silences. `[VERIFIED]`

**F-140-11 — Neither firmware CI workflow runs the 3rd/4th (or a 5th) native env.**
`build.yml:142,155` and `beta-build.yml:122,128` run `native` and `native_nodevtools` only.
`[VERIFIED]`

**F-140-12 — App CI lints `firestarter/ tests/` but not `tools/`.** `ci.yml:81,84` run
`ruff check` / `ruff format --check` on `firestarter/ tests/`; `check_mypy_watermark.py` follows.
A DB-half gate placed in `tests/` is linted and type-watermarked; one placed in `tools/` is neither.
Coverage gate is `--cov-fail-under=70` on `firestarter` only. `[VERIFIED]`

---

## Runtime State Inventory

*Omitted deliberately — Phase 140 is additive (new files, new gates, new test env) and changes no
name, no stored key, no service configuration and no OS registration. The one state-adjacent question
that would normally live here — "does any persisted value feed the new table?" — is answered by
F-140-04: `handle->pulse_delay` comes from the wire on every command and the table stores no pulse.*

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | The Intel "Intelligent Programming Algorithm" applies a 1 ms pulse up to 25 times followed by an overprogram pulse of `3 × N × 1 ms`. No Intel datasheet with a readable pulse-count flowchart was obtainable this session (the Intel 27C010 PDF has no text layer and its rendered pages carry no algorithm flowchart; the 2764A/27512 sheets are not in the corpus). | Datasheet Attribution Matrix (`0x07 overprogram_factor`, `overprogram_cap_us`) | `0x07`'s `overprogram_factor = 3` and the 75 ms cap would lose their only named family basis. Mitigation: TABLE-04 wording must say "Intel Intelligent Programming family — formula not verified against a primary Intel datasheet in this research pass" rather than citing a document that was not read |
| A2 | `check_build_warnings.py`'s native rule (`<= total_watermark`) counts **all** warnings, so any new warning kind — not just macro redefinitions — breaks it. Inferred from `size_baseline.json:warnings.policy.native_rule` plus the counting_command note that the two counts are identical today; the code path was read only in outline. | Pitfall 1 | If the rule counted only redefinitions, a non-redefinition warning would slip through. Low impact — the recommendation (avoid `<Arduino.h>`) is safe either way |
| A3 | 1166 is not an exact multiple of 14, so some TUs in the 17-suite `native` env emit a different per-TU count than the 14 measured in `native_trace_v131`. The **delta** for one new both-includes TU is asserted as "≥ 14 per native env", not "exactly 14". | Pitfall 1 | Only affects the precision of the predicted overshoot, not the direction. The gate has zero headroom, so any positive delta is fatal |
| A4 | A `static const … PROGMEM` array with external linkage is collected by `--gc-sections` when unreferenced, exactly as a `static` one is. Standard `-fdata-sections` behaviour; not measured on this tree. | Pitfall 3 | If wrong, Phase 140 would show a ~36-48 B AVR flash delta instead of ≈0 — visible immediately on the first `pio run`, and *smaller* than Phase 141's budget, so it fails safe |
| A5 | PROTOCOLS.md's DB chip counts (170 / 127 / 32) and this session's DB query agree because they measure the same artifact; no separate provenance was established for PROTOCOLS.md's figures. | State of the Art | Cosmetic |
| A6 | `firestarter_app`'s CI `pytest tests/` leg will pick up a new `tests/test_*.py` automatically (no registry). Consistent with `ci.yml:90` (`pytest tests/ …`) and with how the 1539-test baseline is collected. | Validation Architecture | If a conftest `collect_ignore` were armed, a new module could be silently skipped — the gate would pass vacuously. Cheap to disprove: assert the module appears in `pytest --collect-only` output |

---

## Open Questions (RESOLVED)

All four questions below were answered before planning locked; none is still open. Each carries its
resolution, the basis for it, and a pointer to where the decision is recorded.

1. **`0x07`'s `overprogram_factor` — 3 or 0?** → **RESOLVED: `0`.** Operator-delegated and decided
   2026-08-09 during `/gsd-plan-phase 140`.
   - *What we knew:* CONTEXT delegates only `0x08` to research; `PROJECT.md`'s throughput table and
     D-08's phrase "both overprogramming rows" imply `0x07 = 3`. But **all three `0x07` datasheets
     read this session (Winbond W27C512, ST M27C512, Microchip 27C512A) explicitly apply no
     overprogram**, and 113 of the row's 170 chips belong to that generation. The 22 Intel-family
     1 ms parts are the only ones the 3× rule was written for (F-140-05).
   - *What was unclear at research time:* whether the operator wants the row's dominant sub-population to receive an
     unspecified `3 × N × 100 µs` (≤ 7.5 ms) extra pulse in order to be correct for the 22 Intel
     parts, or wants factor 0 with the Intel parts under-served — the exact asymmetry D-06 reasons
     about for `0x08`, arriving on `0x07` instead.
   - *Resolution (2026-08-09, operator decision during `/gsd-plan-phase 140`):* **ship `0`.** Three
     bases: (a) behaviour-preserving — no protocol overprograms today, and
     `src/proms/eprom.cpp:161-178` is retry escalation of `pulse_delay`, not an Intel 3N margin
     pulse, so `3` would be an unvalidated behaviour change to all 170 chips in the row; (b) all
     three `0x07` datasheets read (Winbond W27C512, ST M27C512, Microchip 27C512A) specify no
     overprogram — 113 of 170 chips; (c) it applies D-06's precedent that a primary datasheet beats
     `PROJECT.md`'s derived throughput table. The 22 Intel-family parts become a **recorded, scoped
     divergence** plus a Phase 146 follow-up (F-140-05) — never a silent omission. D-08's
     `overprogram_cap_us = 75000` is unaffected; it is the figure published on gh#15.
   - *Recorded in:* `140-01-PLAN.md` `<locked_values>`; `140-05-PLAN.md`'s
     `0x07 overprogram_factor` citation cell; `140-06-PLAN.md` §1.3 rewrite; `140-07-PLAN.md`
     record §3; `140-VALIDATION.md` § Locked Decisions Carried Into Planning.

2. **Does `overprogram_cap_us` remain in the table if no row has `overprogram_factor > 0`?** →
   **RESOLVED: yes — keep it.** Settled by D-01/D-08; predates this research pass.
   - *What we knew:* TABLE-01 names the column, so it must exist. With factor 0 on `0x08` (settled)
     and possibly on `0x07` (Q1), the cell may be inert on every row.
   - *Resolution:* keep the column. With factor `0` on all three rows the cell is inert
     everywhere, and is cited as reasoned + **explicitly inert** rather than dropped. An
     inert-but-named cell is honest; a missing column is a requirement violation.
   - *Recorded in:* `140-01-PLAN.md` `<locked_values>` (`75000` uniformly on all three rows).

3. **Should the phase commit the datasheet PDFs it cites?** → **RESOLVED: no.**
   - *What we knew:* F-140-08 — no cited corpus resolves on this branch; `W27C512.pdf` (bench-required)
     is untracked. Committing the 0x07/0x08/0x0B set is roughly 1.3 MB.
   - *Resolution:* do **not** commit. Citations are self-describing instead (vendor, part,
     document number, revision/date, section or figure), and the recovery command
     (§ Code Examples, "Recovering the archived datasheet corpus") is reproduced in the sidecar's
     header so a future reader can obtain them. Committing ~1.3 MB of binaries is a repo-weight
     decision that is not this phase's to make.
   - *Recorded in:* `140-VALIDATION.md`; enforced by `140-05-PLAN.md`'s assertion that no
     `datasheets/…` repo path appears in the sidecar (F-140-08: no cited corpus resolves on this
     branch).

4. **Which repo's `tests/` should hold the citation-coverage gate?** → **RESOLVED: the firmware
   repo (`firestarter/tests/`).**
   - *What we knew:* D-14 does not say. The sidecar and the C table are both in `firestarter/`, and
     `pytest tests/ -v` runs in firmware CI (F-140-11 shows the *native* envs are the gap, not the
     Python ones).
   - *Resolution:* the firmware repo — co-located with what it checks (the sidecar and the C table
     both live in `firestarter/`), no cross-repo seam, and `pytest tests/` runs in firmware CI.
   - *Recorded in / implemented by:* `140-05-PLAN.md` —
     `firestarter/tests/test_eprom_params_citations.py` plus
     `firestarter/tests/golden/eprom_params_citations.json`.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO Core | building/running native envs and AVR targets | ✓ | 6.1.19 | — |
| `platform-atmelavr` + avr-gcc | AVR flash/RAM measurement (MERGE-05) | ✓ | 5.2.0 / 7.3.0 | — |
| Unity / ArduinoFake | native suites | ✓ | 2.6.1 / 0.4.0 | — |
| Python 3 + pytest (firmware `tests/`) | D-13 / D-14 gates | ✓ | firmware suite: 227 pass | — |
| Python 3 + pytest (app `tests/`) | D-12 DB-half gate | ✓ | app suite: 1539 pass (CI-replica py3.11) | — |
| `git` | blob-SHA identity pins; recovering the archived datasheets | ✓ | — | fail-closed by design (`test_golden_trace_identity_eprom_v131.py` test 6) |
| `pdftotext` / `pdftoppm` / `pdfinfo` (poppler) | reading the primary datasheets | ✓ | `/usr/bin/*` | — |
| Datasheet corpus | TABLE-04 attribution | **partial** | 3 tracked in `firestarter_app/`; 4 untracked; 21 on the v1.16 branch only | `git show v1.16-…:datasheets/…` (documented in §Code Examples) |
| Bench hardware (W27C512 / TMS27C512, AM27C020, M2716/M2732) | — | **n/a** | — | **Not needed by Phase 140** — this phase writes data, gates and one native test. Bench work is Phase 145 |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** the datasheet corpus (recoverable from the v1.16 branch; the
2516 sheet has no text layer and must be rendered to images).

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Firmware native (C++) | Unity 2.6.1 via PlatformIO `test_framework = unity`; config `firestarter/platformio.ini` |
| Firmware gates (Python) | pytest; no `conftest.py` anywhere in `firestarter/tests/` (recorded house-rule — every module resolves its own paths) |
| Host gates (Python) | pytest; `firestarter_app/tests/conftest.py` exists; `pyproject.toml` `addopts = -ra -q` |
| Quick run (firmware gates) | `cd /workspaces/firestarter && python3 -m pytest tests/ -q` — baseline **227 passed** |
| Quick run (new native suite) | `cd /workspaces/firestarter && pio test -e native_params_v131` |
| Frozen-baseline guard | `cd /workspaces/firestarter && pio test -e native_trace_v131` — baseline **5 cases / 1 suite**, must stay GREEN (D-10) |
| Pinned envs (must not move) | `pio test -e native` and `pio test -e native_nodevtools` — **141 cases / 17 suites each** |
| Host suite | `cd /workspaces/firestarter_app && python3 -m pytest tests/ -o addopts="" -q` — baseline **1539 passed** (`-o addopts=""` is required; the doubled `-q` otherwise suppresses the count line) |
| Cold size/warning measurement | `rm -rf .pio/build/<env>` then a **single** `pio run -e <env>` / `pio test -e <env>` at a ≥540 s timeout (warm figures under-count: native warm 998 vs cold 1166) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TABLE-01 | Three rows keyed `0x07`/`0x08`/`0x0B`, each carrying the six columns; each protocol resolves to its own distinct row | native unit | `pio test -e native_params_v131` | ❌ Wave 0 |
| TABLE-01 | The struct's field-name list is exactly the frozen six; the row set is exactly three | committed gate (pytest, firmware CI) | `python3 -m pytest tests/test_eprom_params_citations.py -q` | ❌ Wave 0 |
| TABLE-02 | No pulse-width column exists | committed gate | same module — assert no field name matches `(?i)(pulse_(width\|delay\|us)\|fallback_pulse)`; assert the only field containing "pulse" is exactly `max_pulses` (a naive substring test is fooled by `max_pulses` — this is the trap) | ❌ Wave 0 |
| TABLE-02 | The write path still reads `handle->pulse_delay` | behavioural (frozen trace) | `pio test -e native_trace_v131` — the frozen arrays encode the 100/500 µs cadence; GREEN proves `eprom.cpp` is byte-unchanged | ✅ exists |
| TABLE-03 | `pulse_delay == 0` ⇒ 1000/100/500 µs per protocol, **exercised** | native unit | `pio test -e native_params_v131` (3 positive cases) | ❌ Wave 0 |
| TABLE-03 | `pulse_delay != 0` ⇒ untouched (non-vacuity) | native unit | same suite (3 negative controls) | ❌ Wave 0 |
| TABLE-04 | Every `(row, column)` cell has exactly one sidecar citation, and no citation exists for a non-existent cell | committed gate | `python3 -m pytest tests/test_eprom_params_citations.py -q` — bijection assert + non-vacuity (`cells_scanned == 18`, `> 0`) | ❌ Wave 0 |
| TABLE-04 | Each citation is well-formed: either (family + part + doc-number + revision/date + section) **and** the literal D-09 scope sentence, or the exact `"no datasheet basis — reasoned from "` prefix | committed gate | same module | ❌ Wave 0 |
| TABLE-05 | No second firmware algorithm selector: the protocol-branch-site inventory in `src/proms/eprom.cpp` matches the pin exactly, with the allowlist of pre-existing routing predicates | committed gate (pytest, firmware CI) | `python3 -m pytest tests/test_protocol_branch_inventory.py -q` | ❌ Wave 0 |
| TABLE-05 | No new `chip_database.json` field: the union of keys at top level, under `programming` and under `electrical`, with per-key occurrence counts, equals the frozen inventory | committed gate (pytest, app CI) | `cd /workspaces/firestarter_app && python3 -m pytest tests/test_chip_database_field_inventory.py -q` | ❌ Wave 0 |
| *(all)* | Neither pinned native env moved | regression | `pio test -e native` → 141/17; `pio test -e native_nodevtools` → 141/17 | ✅ exists |
| *(all)* | AVR flash/RAM inside the MERGE-05 band, RAM delta exactly 0 | cold measurement + gate | `python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log uno=… …` | ✅ exists |
| *(all)* | Native warning watermark unmoved | cold measurement + gate | `python3 scripts/check_build_warnings.py` on `native` / `native_nodevtools` — expect exactly 1166 each | ✅ exists |

**Explicitly NOT verifiable in CI — stated rather than implied:**

- **`pio test -e native_params_v131` does not run in CI.** Neither `build.yml` nor `beta-build.yml`
  invokes any env beyond `native` and `native_nodevtools` (F-140-11). The TABLE-03 fallback proof is
  a **local, run-by-name obligation** for this phase's verification, and its counts must be recorded
  in the phase record (D-11). The same is true of `native_trace_v131`.
- **`check_size_baseline.py` and `check_build_warnings.py` are blind to the new env** (F-138-05:
  uncaught `KeyError` → exit 1; and no baseline entry → exit 2). Do not pass the env name to either.
- **No bench oracle exists for TABLE-03.** F-140-04: 0 of 329 shipped 27C chips produce
  `pulse_delay == 0`. A bench run cannot reach the fallback; claiming bench coverage for it would be
  false. Phase 145's bench work covers the *loop*, not this branch.
- **The 6.25 V program-VCC and the datasheets' raised-VCC verify passes are unreachable on this
  hardware** and are therefore unverifiable at any level. This is the milestone's evidence ceiling and
  it is the reason D-02 forbids a verify-VCC column.
- **`0x07`'s `overprogram_factor`** cannot be validated by any test in this phase — the table is
  unreferenced by `src/` (D-10). It is a *data correctness* question, settled by attribution and
  operator decision (Open Question 1), not by an assertion.

### Sampling Rate

- **Per task commit:** `python3 -m pytest tests/ -q` in whichever repo the task touched (firmware
  227 → 227+N; app 1539 → 1539+N), plus `pio test -e native_params_v131` for tasks touching the suite.
- **Per wave merge:** `pio test -e native && pio test -e native_nodevtools && pio test -e native_trace_v131 && pio test -e native_params_v131`,
  then `python3 -m pytest tests/ -q` in both repos.
- **Phase gate:** the above, plus a **cold** `rm -rf .pio/build/<env>` + single-invocation
  `pio run -e uno|uno328pb|leonardo` capture feeding `check_size_baseline.py --policy merge05` and
  `check_build_warnings.py`; plus every new gate seen RED on a planted violation and then GREEN
  (D-15).

### Wave 0 Gaps

- [ ] `firestarter/include/eprom_params.h` + `firestarter/src/proms/eprom_params.cpp` — the artifact
      every other item asserts against (TABLE-01/02)
- [ ] `firestarter/test/native/avr/test_eprom_params_v131/{host_stubs.cpp,test_eprom_params_v131.cpp}`
      — covers TABLE-03 (and TABLE-01's row resolution; **do not** mark TEST-01 complete, it is
      Phase 144's)
- [ ] `firestarter/platformio.ini` `[env:native_params_v131]` — the suite is invisible until it
      appears in a positive allowlist
- [ ] `firestarter/tests/golden/eprom_params_citations.json` — the D-14 sidecar (18 cells)
- [ ] `firestarter/tests/test_eprom_params_citations.py` — TABLE-04 + TABLE-01/02 structural gate
- [ ] `firestarter/tests/golden/protocol_branch_inventory.json` — the D-13 pin (4 sites + allowlist)
- [ ] `firestarter/tests/test_protocol_branch_inventory.py` — TABLE-05 firmware half
- [ ] `firestarter_app/tests/golden/chip_database_field_inventory.json` — frozen key set + counts
- [ ] `firestarter_app/tests/test_chip_database_field_inventory.py` — TABLE-05 DB half
- [ ] Planted-violation fixtures/runs for all three new gates (D-15) — each must be **seen RED**, and
      the RED output captured verbatim in the plan's SUMMARY, before any GREEN is believed
- [ ] Framework install: **none needed**

**Frozen key inventory measured this session** (`chip_database.json`, 746 chips, 59 manufacturers) —
the exact content the DB-half gate should pin:

| Level | Keys → occurrence count |
|---|---|
| top level | `electrical` 746, `part_number` 746, `pinout` 746, `programming` 746, `support_status` 746, `unsupported_reason` 10, `datasheet` 2, `provenance` 2, `source` 2, `verification_note` 2, `verification_status` 2 |
| `programming` | `algorithm` 746, `chip_id_check` 746, `chip_id_value` 746, `pulse_duration` 746, `infoic_page_size_raw` 744, `protect_off_before` 744, `protect_on_after` 744, `page_size` 2 |
| `electrical` | `pin_count` 746, `size_bytes` 746, `type` 746, `vcc` 746, `vdd` 746, `vpp` 746, `vpp_mv` 746 |
| 27C protocol counts | `algorithm` 7 → **170**, 8 → **127**, 11 → **32** |

*Pin the counts, not just the key names: a field added to a subset (as `page_size` and the five
sparse top-level keys already are) would otherwise slip past a names-only assertion.*

---

## Security Domain

`security_enforcement` is not set to `false` in `.planning/config.json`, so this section is included.
This is embedded firmware data plus test/gate tooling; most ASVS categories are structurally
inapplicable, and saying so is more honest than manufacturing coverage.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No user, session or credential exists anywhere in this phase's surface |
| V3 Session Management | no | The serial protocol is a local, single-peer, unauthenticated link by design |
| V4 Access Control | **indirectly** | `is_memory_cmd()` (`firestarter.h:133-147`) is documented in-tree as an **access-control gate**, not hygiene: it decides which commands may call `configure_memory()` and therefore energise the 12 V VPP regulator. Phase 140 must not widen it, and D-13's gate is the mechanism that would notice |
| V5 Input Validation | **yes** | `handle->protocol` arrives from untrusted JSON (`json_parser.c:503`). D-05's NULL-return-and-fail-closed is the correct control and mirrors `memory.cpp:134-138`'s generic fail-closed guard. **Never** fall back to the `0x07` row for an unrecognised protocol |
| V6 Cryptography | no | None used or added |
| V14 Configuration | **yes** | The gates are themselves a supply-chain-integrity control: a gate that fails open (Phase 117 ×4) or scans nothing and exits 0 (`check_permitted_claims.py`'s `_HERE`) is worse than no gate, because it manufactures false assurance |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Unrecognised `protocol` silently routed to a default row ⇒ 13 V through the wrong path onto a 5 V part | Tampering / **Damage to physical asset** | D-05: return NULL, caller fails closed, zero hardware side effects. This is the v1.20 shape and it is a hardware-safety control, not a style choice |
| Out-of-range `pulse_delay` (wire field is uint16 ⇒ 65535 µs reachable) driving an unbounded overprogram pulse | Denial of Service / physical damage | D-08's clamp: `min(3 × N × pulse, overprogram_cap_us)`. Consumed in Phase 141; the *value* ships here |
| A gate that passes with nothing scanned | Repudiation | Explicit target resolution + a non-zero scanned count in the PASS line (`139-check-claims.py:271,321`), and a planted-violation RED run (D-15) |
| A gate silenced by regenerating its own baseline | Tampering | The TABLE-05 DB-half inventory must be committed in the test module / a golden JSON that regenerating `chip_database.baseline.json` does not touch (F-140-10) |
| `delayMicroseconds()` above its 16383 µs ceiling (75 ms overprogram) | DoS / undefined timing | LOOP-07's 32-bit-safe helper — **Phase 141**, not here; the cap value ships here |

---

## Sources

### Primary (HIGH confidence)

**In-tree, read this session:**
- `firestarter/src/proms/eprom.cpp` (full, 332 lines) — `:20`, `:41-77`, `:71-76`, `:143-193`, `:145`, `:155`, `:163`, `:177`, `:181-192`, `:209-272`, `:218`, `:320`
- `firestarter/src/proms/memory.cpp` (full, 390 lines) — `:93`, `:95-138`, `:115`, `:162-171`, `:301`
- `firestarter/include/firestarter.h` — `:32` handle globals context, `:133-147` `is_memory_cmd`, `:188-219` `firestarter_handle_t`
- `firestarter/include/proto_constants.h` — `:18-29`
- `firestarter/include/memory_utils.h:24-28` — `using_p1_as_vpp`
- `firestarter/include/rurp_platform_compat.h` (full) — PROGMEM/`pgm_read_*`/`memcpy_P` host shims
- `firestarter/include/avr/pgmspace.h` — `#include_next` / compat fork
- `firestarter/src/json_parser.c` — `:56-79` PROGMEM precedent, `:81-89` reset set, `:114-116` access idiom, `:304-305` `get_delay`, `:313` `get_algorithm`
- `firestarter/platformio.ini` (full, 329 lines) — `:16`, `:69-164`, `:166-253`, `:255-291`, `:293-328`
- `firestarter/test/native/avr/_shared/host_stubs_common.inc` — `:22-32`, `:59-197`
- `firestarter/test/native/avr/_shared/eprom_v131_expected.h` — API and fixture shape
- `firestarter/test/native/avr/test_trace_eprom_v131/{test_trace_eprom_v131.cpp,host_stubs.cpp}`
- `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp`
- `firestarter/tests/test_golden_trace_identity_eprom_v131.py`, `tests/test_checker_convention.py`
- `firestarter/scripts/check_size_baseline.py:100,107,269,421,442`; `scripts/check_build_warnings.py`
- `firestarter/scripts/baseline/size_baseline.json` (warnings block), `size_baseline_v131.json` (meta, avr_targets, native_envs, deltas_vs_base01)
- `firestarter/doc/PROTOCOLS.md` §§1.3-1.5 + the protocol table
- `firestarter/CLAUDE.md` §Protocol Dispatch, §Algorithm Handlers, §Native (Host) Test Environment
- `firestarter/.github/workflows/{build.yml,beta-build.yml}`
- `firestarter_app/firestarter/database.py:128-144, 405-424, 545-570`
- `firestarter_app/firestarter/data/chip_database.json` (field inventory + per-protocol pulse distribution, queried through the production parser)
- `firestarter_app/tools/diff_db.py:292-312, 373-392`; `tests/scan_paths.py`; `tests/test_dev_gate_reads_no_firmware_source.py`; `tests/test_diff_db_gate.py`
- `firestarter_app/pyproject.toml` `[tool.ruff]` / `[tool.mypy]`; `.github/workflows/ci.yml:56-128`
- `~/.platformio/platforms/atmelavr/builder/frameworks/arduino.py:98,99,111`

**Planning record:**
- `.planning/phases/140-parameter-table/140-CONTEXT.md` (full) and `140-DISCUSSION-LOG.md` (full)
- `.planning/REQUIREMENTS.md` §Parameter Table (TABLE-01…05), §Per-Byte Program Loop, TEST-01…08
- `.planning/ROADMAP.md` §Phase 140, §Phase 141, §Phase 142
- `.planning/PROJECT.md` §Current Milestone v1.31 (C1/C2/C3, D-01, D-02, target features, throughput table, evidence ceiling)
- `.planning/seeds/27c-algorithm-fidelity-param-table-refactor.md:145-215, 240-241`
- `.planning/phases/138-preconditions-baseline/138-BASELINE.md` §5 (counts, watermarks, gate verdicts), §6 (pulse distribution), §7 (F-138-02, F-138-05, F-138-06, F-138-08)
- `.planning/phases/139-gh-15-correction-outward/139-check-claims.py` (gate pattern)

**Primary datasheets (all read in full this session — see §Datasheet Attribution Matrix for the
verbatim quotations and provenance):** Winbond W27C512 Rev A4 (Nov 1999); ST M27C512 Rev 3 (May 2007);
Microchip 27C512A DS11173G (2004); AMD Am27C020 (FINAL); ST M27C1001; Winbond W27C020 (Preliminary);
Intel 27C010; TI TMS 2516-25/35/45 JL (Dec 1979, rev. May 1982).

### Secondary (MEDIUM confidence)
- `https://ww1.microchip.com/downloads/en/DeviceDoc/11173G.pdf` — official Microchip URL; text
  extracted and quoted directly
- `https://www.ardent-tool.com/datasheets/Intel_27C010.pdf` — third-party archive of an Intel
  document; image-only, pages rendered and read. Treated as MEDIUM because the archive's fidelity to
  the original was not independently corroborated

### Tertiary (LOW confidence — flagged, not relied upon)
- WebSearch result summaries asserting "up to 10 (ten) 100-µs pulses" for a 27C010 and naming
  "SNAP! Pulse Programming" — not used for any table value; the corresponding Microchip figure was
  instead confirmed by reading DS11173G directly
- The Intel "Intelligent Programming" 1 ms / 25 / `3N ms` formula — training knowledge, recorded as
  assumption **A1**, not cited as a datasheet fact

---

## Metadata

**Confidence breakdown:**
- Firmware/test/gate infrastructure: **HIGH** — every figure in this document was measured in-tree
  this session (cold `pio test` run, warning attribution by TU, DB query through the production
  parser, `git ls-tree`/`git ls-files`, builder-flag grep), not recalled
- Datasheet attribution for `0x08` and `0x0B`: **HIGH** — three independent vendors on `0x08`
  (including the exact 27C010-class part D-06 names), and the TI TMS 2516 AC table on `0x0B`
- Datasheet attribution for `0x07`: **MEDIUM** — `max_pulses`, `verify_mode` and `vpp_path` are
  HIGH; `overprogram_factor` carries assumption A1 and Open Question 1
- Pitfalls: **HIGH** — 6 of the 8 are measured facts with commands and line numbers; Pitfalls 2 and 3
  rest on standard, documented compiler behaviour (A2, A4)

**Not researched (deliberately, per CONTEXT):** alternatives to any locked decision; the Phase 141
loop; the Phase 142 VPP mask rewrite; `--pulse-us`; the trace/flash re-baselining; the six reviewed
todos.

**Research date:** 2026-08-09
**Valid until:** 2026-09-08 for the datasheet attribution (stable, decades-old documents); **7 days**
for the infrastructure figures — the 1166 warning watermark, the 141/17 counts, the 227/1539 suite
counts and the MERGE-05 headroom all move the moment any plan lands, and the headroom is already
known to be smaller at the live `beta` tip (F-138-02).
