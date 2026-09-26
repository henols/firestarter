# Phase 140: Parameter Table - Context

**Gathered:** 2026-08-09
**Status:** Ready for planning

<domain>
## Phase Boundary

One `const`, `protocol_id`-keyed **shape** table for the three 27C protocols (`0x07`, `0x08`,
`0x0B`), every value attributed, plus the machinery that proves it: a test that exercises the
`pulse_delay == 0` fallback, a gate that proves no unattributed number ships, and a gate that proves
no second dispatch key and no new `chip_database.json` field were introduced.

**Requirements:** TABLE-01, TABLE-02, TABLE-03, TABLE-04, TABLE-05.

**This phase writes DATA and GATES, not BEHAVIOUR.** `firestarter/src/proms/eprom.cpp` is
**byte-unchanged** by this phase (D-06). Nothing in `src/` reads the table yet — Phase 141 wires it.
The programming loop, the VPP routing rewrite and the host timeout work are Phases 141, 142 and 143
respectively and are explicitly *not* started here.

**This phase is DUAL-REPO.** The TABLE-05 gate splits: the firmware half commits into
`firestarter/`, the `chip_database.json` half commits into `firestarter_app/` (D-11). The planner
MUST express this as `commits_land_in:` naming **both** submodules — never inferred from
`files_modified`, which under-detects when a worktree leaves a submodule empty.

**Not in this phase:** the per-byte pulse→verify loop (Phase 141), removal of
`program_mismatched_bytes()` / `verify_and_update_mask()` / `NUMBER_OF_RETRIES` (Phase 141), the
VPP/VPE mask rewrite and disable-on-every-exit (Phase 142), `--pulse-us` and host timeout
(Phase 143), the frozen-vs-new golden-trace diff and flash-delta reconciliation (Phase 144).

</domain>

<decisions>
## Implementation Decisions

### Column set

- **D-01: The table ships SIX columns — the five TABLE-01 names, plus `energy_cap_us`.**
  `energy_cap_us` = `0` on `0x07` and `0x08` (no cap), `50000` on `0x0B`. TABLE-01 says the table
  "carries rows … with" those five columns; it does not say *only* those five, so a sixth is
  additive rather than a violation and needs no REQUIREMENTS amendment.
  **Rationale:** LOOP-04 requires "accumulated program time per byte capped at 50 ms" on `0x0B`, and
  none of the five named columns can express it. A dedicated column is self-documenting, gives
  TABLE-04 one cell to cite, and lets Phase 141's loop read it like every other column.
  *Rejected:* deriving `max_pulses = 50000 / pulse_delay` (makes `max_pulses` mean a count on two
  rows and a derived budget on the third, and smuggles the pulse back into the table's semantics);
  overloading `overprogram_cap_us` so its meaning flips with `overprogram_factor` (a field that means
  two things is exactly the unattributable number TABLE-04 exists to stop); keeping the cap as an
  `if (protocol == PROTO_EPROM_24PIN)` inside Phase 141's loop (plants a second protocol test in the
  write path — the shape TABLE-05 and milestone D-01 both remove).

- **D-02: `verify_mode` encodes WHEN to verify, never at what VCC.** Two values:
  `VERIFY_PER_PULSE` (read the byte back after every pulse; this is what drives the loop's exit) and
  `VERIFY_PER_PULSE_PLUS_FINAL` (the same, plus one full-array read-back pass after the block
  completes). Which row gets which is a TABLE-04 research question against the primary datasheets.
  **Hard constraint attached to this column:** it may **never** encode a verify VCC margin. The
  datasheets specify verify at raised VCC for threshold margin; the RURP has no VCC-raise path (the
  ~6.25 V ceiling), so such a column could only record a value the firmware cannot act on. The
  citation for this column must say so explicitly — this is one of the concrete places the evidence
  ceiling bites, and it belongs in the record here rather than only in Phase 146's ledger.
  *Rejected:* a single constant value across all three rows (dead PROGMEM, and TABLE-04 would have
  to cite "no datasheet basis" for a column that does nothing); encoding verify VCC (ships a
  knowingly-inert field).

- **D-03: The `pulse_delay == 0` fallback constants STAY in `configure_eprom`'s switch (`eprom.cpp:71-76`) — no pulse number enters the table.** Literal compliance with TABLE-02 ("the
  table has no pulse-width column") and with milestone D-01 ("the database owns the pulse"). A
  column named `fallback_pulse_us` *is* a pulse-width column on any plain reading, and gh#15's
  correction — posted publicly in Phase 139 — just told the world the table has no pulse column.
  Keeping the fallback visibly a fallback also stops a reader mistaking it for the algorithm's pulse.
  *Rejected:* a `fallback_pulse_us` column plus a REQUIREMENTS amendment; moving the constants to
  named `#define`s beside the table (two structures then describe one protocol).

- **D-04: Storage is `PROGMEM`, and this is forced, not preferred.** MERGE-05 requires AVR RAM delta
  **exactly 0** against Phase 138's baseline. On AVR a `const` struct array without `PROGMEM` lands
  in `.data` and is copied into RAM at startup, so a plain `const` table fails the gate on arrival.
  Follow the existing precedent: `static const key_parser_t key_parsers[] PROGMEM` at
  `firestarter/src/json_parser.c:164`. Uno-class flash headroom is **42 B (`uno`) / 36 B
  (`uno328pb`)** against the 64 B MERGE-05 band at the fork base — and materially less at the live
  `beta` tip (F-138-02: 8 B / 2 B). Budget accordingly.

- **D-05: A lookup that finds no row returns NULL and the caller fails closed, with zero hardware side effects.** Matches the firmware's standing fail-closed invariant (`memory.cpp` steps 6a/6b/7,
  Phase 64 / v1.20). `configure_eprom` is only reachable with `0x07`/`0x08`/`0x0B` today, but the
  guard survives a future dispatch edit the compiler cannot catch.
  *Rejected:* falling back to the `0x07` row (mirrors today's `default: 1000` but would silently
  route 13 V through the drop resistor for an unrecognized protocol — the exact silent-wrong-hardware
  shape v1.20 removed); a compile-time-only `static_assert` (proves nothing at runtime and the gate
  would have nothing to assert against).

### Row values & attribution

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
  *Rejected:* deciding it now from either planning document (decides a silicon question from prose,
  the exact move TABLE-04 exists to prevent); splitting `0x08` into more than one row (a second row
  keyed on anything but `protocol_id` is a second dispatch key, forbidden by TABLE-05) — though if
  research finds the 32-pin family genuinely spans both Intelligent and Quick-Pulse silicon, that is
  a **finding for Phase 146**, recorded rather than forced into a wrong single value.

- **D-07: On `0x0B`, `max_pulses` and `energy_cap_us` BOTH bind — whichever trips first.**
  `energy_cap_us = 50000` is the intended budget and normally binds; `max_pulses` is a generous
  structural backstop that guarantees termination at a pathological pulse width (Phase 143's
  `--pulse-us 1` would otherwise mean 50 000 iterations on a single byte). Either trip is the same
  LOOP-05 hard-fail, and the error reports **which** limit tripped. TABLE-04 cites the cap to the
  2716-class datasheet and marks `max_pulses` on this row `"no datasheet basis — reasoned from:
  termination bound"`.
  *Rejected:* energy-cap-only with `max_pulses = 0` as a sentinel (the column then means two things
  across rows, and termination depends entirely on `pulse_delay` being sane, which `--pulse-us` can
  violate); count-only (silently under-programs every `0x0B` chip whose DB pulse is below 500 µs and
  discards milestone D-02's entire rationale for the 50 ms figure — at 200 µs, 100 pulses is 20 ms,
  40% of the datasheet budget).

- **D-08: `overprogram_cap_us = 75000` on both overprogramming rows, and the cap CLAMPS.** The
  overpulse is `min(3 × N × pulse, cap)`. 75 ms is `3 × 25 × 1000 µs`, the Intelligent worst case,
  and is the exact figure C3 was publicly stated against on gh#15 ("the 32-bit-safe helper is needed
  for the 75 ms overprogram pulse") — keeping it uniform keeps that public statement true. On `0x08`
  at the modal 100 µs it never binds; it exists as a hardware-safety ceiling against a large DB pulse
  or a `--pulse-us` override (the minipro wire field is uint16, so 65535 µs is reachable —
  `3 × 25 × 65535 ≈ 4.9 s` without a cap). Cited as **reasoned**, not datasheet-derived.
  *Rejected:* hard-failing instead of clamping (turns a legal chip with a 3000 µs DB pulse into a
  refusal, and LOOP-03's own text says "capped at `overprogram_cap_us`"); per-row caps
  (`0x08 → 7500` would clamp 23 of the 127 measured `0x08` chips routinely, turning a safety ceiling
  into a truncation).

- **D-09 (Claude's call, delegated): a row's citation is TWO-PART, with an explicit scope clause.**
  Each row cites **(a)** the vendor algorithm family by name — Intel Intelligent Programming, Intel
  Quick-Pulse, classic 2716 50 ms programming — because that is what `protocol_id` actually names,
  and **(b)** one named representative part: manufacturer, part number, datasheet revision/date,
  chosen to be a part Phase 145 can actually bench (`0x07` → W27C512 / TMS27C512, the *required*
  bench coverage; `0x08` → AM27C020; `0x0B` → M2716 / M2732). Every citation carries the literal
  scope sentence: *"representative of this row; not asserted true of all N chips carrying this
  `protocol_id`."*
  **Rationale:** family-alone is unverifiable at the bench; part-alone overclaims across 170 / 127 /
  32 chips. Together a reader can check the number against a real document *and* check the firmware
  against real silicon, while the scope clause stops it becoming a claim about 170 parts that nothing
  in this milestone can support. Values with nothing behind them take the `"no datasheet basis —
  reasoned from X"` form instead.
  *Rejected:* enumerating every distinct value across all 329 chips (TABLE-04 asks for attribution,
  not a survey).

### Seam with Phase 141

- **D-10: Phase 140 ships DATA + GATES + TEST only. `eprom.cpp` is byte-unchanged.**
  `native_trace_v131` asserts **full ordered positional equality** against Phase 138's frozen trace
  for all three protocols; leaving `eprom.cpp` alone keeps it GREEN through this phase, so the first
  legitimate trace movement is Phase 141's — diffed deliberately in Phase 144 / TEST-06, which is
  where the roadmap put it.
  *Rejected:* rewiring the duplicated `0x0B || FLAG_VPE_AS_VPP` VPP branch at `eprom.cpp:145` and
  `:218` now (any non-bit-identical mask emission turns `native_trace_v131` RED in Phase 140 and it
  stays RED for three phases); rewiring **and** re-freezing the fixture inside Phase 140 (a fixture
  re-frozen by whichever phase breaks it stops being evidence).

  **Consequence the planner must carry:** the table is unreferenced by `src/`, so
  `eprom_params_for()` and the table are garbage-collected out of the AVR image. **Phase 140's AVR
  flash delta is therefore expected to be ~0, and the real flash cost lands in Phase 141.** State
  that expectation explicitly in the phase record so Phase 144 / TEST-08 reconciles the total instead
  of reporting a surprise. Do **not** force a reference with `__attribute__((used))` — that burns
  scarce Uno-class headroom on code nothing calls.

- **D-11: The TABLE-03 fallback test runs in a FIFTH dedicated native env, on the `native_trace_v131` precedent.** Both pinned envs (`native`, `native_nodevtools`) are asserted at
  **exactly 141 cases / 17 suites** by the live `scripts/baseline/size_baseline.json`, and
  `check_size_baseline.py`'s default mode is strict byte-identity — adding one case to any of those
  17 suites turns that gate RED. The new env names **only** its own suite in `test_filter`, is never
  folded into either pinned env's `test_filter`, and is never added to `default_envs` (a
  `main()`-less `pio run` target fails to link).
  **Known cost, inherited from finding F-138-05 and accepted, not fixed:** `check_size_baseline.py`
  hardcodes `NATIVE_ENVS = ("native", "native_nodevtools")` and `compare_native` does a bare
  dictionary lookup, so an unknown env name raises an **uncaught KeyError (exit 1)** — a false
  regression signal, not the documented exit-2. Both live gates are therefore blind to the new env.
  **The suite must be run explicitly, by name, in this phase's own verification**, and its counts
  recorded in the v1.31 baseline record.
  *Rejected:* adding the test to `test_val_eprom` and re-baselining the live `size_baseline.json`
  (Phase 138 created `size_baseline_v131.json` precisely so nothing moves the live baseline before
  Phase 144); folding it into `native_trace_v131`'s suite (mixing a behavioral test into the frozen
  fixture suite muddies what a RED there means in Phase 144).

### Proof machinery

- **D-12: TABLE-05 splits into TWO gates, each committed in the repo it can actually see.** The
  firmware half lands in `firestarter/`; the `chip_database.json` half lands in `firestarter_app/`.
  Neither needs a cross-repo path seam, so neither can fail open when the other repo moves.
  **Rationale:** an app-side gate scanning firmware source is the exact shape that **failed open four
  times in Phase 117** when firmware symbols were renamed. A meta-repo script reading both working
  trees runs in no CI leg of either sub-repo, making it a local-run obligation rather than the gate
  TABLE-05 asks for.
  **Planner consequence:** Phase 140 is dual-repo — `commits_land_in:` names both submodules. The
  DB-half gate is scheduled **here**, not deferred to Phase 143.

- **D-13: The firmware half asserts a PINNED INVENTORY of protocol-branch sites, with an allowlist.**
  The gate enumerates every site in the EPROM path that branches on `handle->protocol` — today:
  `configure_eprom`'s pulse fallback switch (`:71-76`), `eprom_write_execute` (`:145`),
  `eprom_check_vpp` (`:218`), plus the new table — and pins that inventory. A **new** branch site, or
  a branch keyed on **any other** handle field, fails the gate.
  **Rationale:** it is concrete and greppable, it catches a second selector introduced in Phases
  141-142 and not merely in 140, and it makes those phases' removals visible as inventory shrinkage
  rather than as prose claims.
  *Rejected:* asserting only that no second protocol-**keyed data structure** exists (says nothing
  about a plain `if`/`switch`, which is how every existing selector in `eprom.cpp` is written);
  pinning `memory.cpp`'s dispatch chain (upstream of this phase — it would pass unchanged even if
  Phase 140 added a second selector inside `eprom.cpp`).

- **D-14: TABLE-04's citations live in a MACHINE-READABLE SIDECAR, gate-enforced; the C table carries short comments pointing at it.** One entry per `(row, column)` cell — family, representative part,
  datasheet revision, the D-09 scope clause, or the `"no datasheet basis — reasoned from X"` form. A
  gate asserts the entry set **exactly** covers the table's cells: every value cited, and no citation
  for a value that does not exist. That turns "no unattributed number ships" into an exit code rather
  than an inspection. The per-row comment in the header keeps a firmware reader from being stranded.
  *Rejected:* inline C comments only (TABLE-04's guarantee would then rest on inspection — exactly
  what TABLE-05's own wording rejects); a prose markdown doc only (nothing detects a value changing
  without its citation following, which is the drift the whole column set exists to prevent).

- **D-15 (house rule, restated because it binds here): every gate this phase authors must be SEEN TO FAIL on a planted violation before any pass is believed.** Phase 138's Run 1 planted-failure
  discipline is this milestone's standing style. Three specific traps this project has already hit,
  all of which apply to the gates in D-12/D-13/D-14:
  1. `check_permitted_claims.py`'s `_HERE` resolved to the **checker's own** phase directory —
     naive cross-phase reuse scanned nothing and exited 0, a false green. Any new checker must
     resolve its targets explicitly and assert it scanned a non-zero number of files.
  2. A **pre-authored gate leg can be unreachable** — a RED proves nothing until the leg has also
     been seen to pass; when fixing, fix the locator, not the assertion.
  3. A planted break must be placed where the gate can actually reach it — a break planted behind a
     manifest/allowlist dies before the gate runs.

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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone decision record (locked — do not re-litigate)
- `.planning/PROJECT.md` §"Current Milestone: v1.31 27C Programming-Algorithm Fidelity (gh#15)" —
  the C1/C2/C3 correction table, milestone **D-01** (protocol owns *shape*, database owns the
  *pulse*), **D-02** (`0x0B`'s 50 ms energy cap, reasoned not derived), the target-features list
  naming this phase's six columns, the expected-throughput table, and the **~6.25 V evidence
  ceiling**. **This document contains the `0x08` overprogram contradiction D-06 resolves** — its
  prose and its own throughput table disagree.
- `.planning/ROADMAP.md` §"Phase 140: Parameter Table" — the four success criteria and the
  `Depends on: Phase 139` line; and §"Phase 141: Per-Byte Program Loop" — read this too, because
  LOOP-03/LOOP-04 are what the `overprogram_*` and `energy_cap_us` columns must be shaped to serve.
- `.planning/REQUIREMENTS.md` §"Parameter Table" lines 169-179 — TABLE-01…05 verbatim.
- `.planning/seeds/27c-algorithm-fidelity-param-table-refactor.md` — the `/gsd-explore` pass
  (commit `c60543c5`) that produced C1/C2/C3.
- `.planning/phases/139-gh-15-correction-outward/139-CONTEXT.md` — Phase 139's D-04 in particular:
  the public gh#15 comment publishes this table's **shape** and marks **every numeric row
  "proposed"**. Per-value attribution is *this* phase's job. Do not present a proposed row as
  datasheet-attributed, and do not contradict what was published.
- `.planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md` — the frozen, posted text.
  What this phase ships must reconcile against it in Phase 146 / CLOSE-04.

### Firmware code this phase touches or must not touch
- `firestarter/src/proms/eprom.cpp` — **read-only in this phase (D-10).** `:20`
  `NUMBER_OF_RETRIES`; `:71-76` the `pulse_delay == 0` fallback switch (**stays**, D-03); `:145` and
  `:218` the duplicated `0x0B || FLAG_VPE_AS_VPP` VPP branch (Phase 142's, inventoried by D-13);
  `:177` the adaptive growth formula (Phase 141's).
- `firestarter/include/proto_constants.h` — the `PROTO_EPROM_28PIN` / `_32PIN` / `_24PIN` tokens the
  table is keyed by. The label IS the number; do not introduce a new naming layer.
- `firestarter/src/proms/memory.cpp:115` — the only call site that reaches `configure_eprom`, and the
  fail-closed chain (steps 6a/6b/7) D-05 mirrors.
- `firestarter/include/firestarter.h` — `firestarter_handle_t`, `protocol`, `pulse_delay`, `pins`.
- `firestarter/src/json_parser.c:164` — `static const key_parser_t key_parsers[] PROGMEM`, the
  storage precedent D-04 follows.
- `firestarter/CLAUDE.md` §"Protocol Dispatch", §"Algorithm Handlers", §"Native (Host) Test
  Environment" — the dispatch contract and the positive-allowlist `test_filter` / `-I` plumbing D-11
  must extend. **Its Algorithm Handlers table will need updating if any row value changes.**

### Baselines and gates this phase must not disturb
- `firestarter/scripts/baseline/size_baseline.json` — the **live** baseline. Asserts exactly
  **141 cases / 17 suites** on both pinned native envs. D-11 exists because of this file.
- `firestarter/scripts/baseline/size_baseline_v131.json` — **frozen for Phase 144 / TEST-08**; read
  only via an explicit `--baseline` argument, never the default seam. Its `meta.deltas_vs_base01`
  block carries the operative Uno-class headroom: **+22/64 B (`uno`), +28/64 B (`uno328pb`)**,
  **−56 B (`leonardo`, must-not-grow)**; RAM delta must be **exactly 0**.
- `firestarter/scripts/check_size_baseline.py` — `NATIVE_ENVS` is hardcoded; an unknown env name
  raises an uncaught KeyError (exit 1), not exit 2. The F-138-05 trap D-11 accepts.
- `firestarter/test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp` — asserts **full
  ordered positional equality** against the frozen pre-change trace. D-10 keeps it GREEN.
- `firestarter/platformio.ini` §`[env:native_trace_v131]` (lines ~293-328) — the **template** for
  D-11's fifth env, including the HARD CONSTRAINT comment block explaining why it must never be
  folded into either pinned env.
- `.planning/phases/138-preconditions-baseline/138-BASELINE.md` — PREP-03's record; §7 finding
  **F-138-02** (headroom at the live `beta` tip is 8 B / 2 B, not 42/36) and **F-138-05** (both live
  gates are blind to a non-pinned native env).
- `.planning/phases/138-preconditions-baseline/138-02-PULSE-DISTRIBUTION.md` — the live per-protocol
  pulse distributions (`0x07` n=170, `0x08` n=127, `0x0B` n=32) that D-06/D-07/D-08's reasoning
  rests on. Re-run `138-pulse-distribution.py` rather than re-deriving by hand.

### Host repo (the TABLE-05 DB half)
- `firestarter_app/firestarter/data/chip_database.json` — **GENERATED, never hand-edited.** The
  gate asserts its field set is unchanged; it must not become an excuse to edit it.
- `firestarter_app/firestarter/database.py:128` — `_parse_pulse_duration`, the `pulse_duration`
  string → `pulse-delay` int-µs layer; and `:417`, `:555` where `pulse-delay` reaches the wire.
- `firestarter_app/doc/infoic-field-dictionary.md:210-217` — where C1's 500 µs adjudication lives.

### Prior-art gates (reuse the pattern, not the file — D-15)
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/check_permitted_claims.py` —
  the `_HERE`-resolves-to-the-checker's-own-phase-dir landmine. Repoint targets explicitly and assert
  a non-zero scanned count.
- `.planning/phases/139-gh-15-correction-outward/139-check-claims.py` — the Phase-139-scoped
  re-derivation of that checker, including its planted-violation run.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`static const key_parser_t key_parsers[] PROGMEM` (`src/json_parser.c:164`)** — the firmware's
  existing const-table-in-PROGMEM pattern, including the `pgm_read_*` access idiom. D-04's model.
- **`[env:native_trace_v131]` (`platformio.ini:293-328`)** — a complete worked instance of adding a
  native env that names only its own suite, stays out of `default_envs`, and is deliberately
  excluded from both live gates, with the reasoning written into the file as comments. D-11 copies
  this wholesale, including the comment discipline.
- **`test/native/avr/_shared/host_stubs_common.inc`** — the shared native stub layer; a new suite
  extends it rather than re-deriving `rurp_*` stubs.
- **`memory.cpp`'s fail-closed chain (steps 6a/6b/7)** — the exact idiom D-05 mirrors: an
  unrecognized value reaches an error with zero hardware side effects, never a default behavior.
- **`138-pulse-distribution.py`** — runnable, already proved its own capacity to fail (the planted
  Run 1). Re-run it; do not re-measure the distribution by hand.

### Established Patterns
- **`protocol_id` is the sole dispatch key, end to end.** No secondary axis, no legacy fallback
  (v1.20 removed it). TABLE-05 is the mechanical restatement of that invariant.
- **The label IS the number.** `PROTO_*` tokens are a legibility layer only (v1.19 / GATE-01); a new
  naming layer that changes or shadows a dispatch value is out of bounds.
- **A gate that has only ever passed is untrusted.** Plant a violation, watch it go RED, then fix it.
- **Cite by commit or `file:line`, never by recollection.**
- **`messages.h` is codegen-generated and ID-only** — if this phase needs a new error message for the
  fail-closed NULL row, it is authored in the meta repo's `messages.toml` and regenerated, never
  hand-edited in the firmware.
- **Baselines are frozen deliberately.** Phase 138 created a sibling rather than moving the live one;
  this phase inherits that discipline.

### Integration Points
- `configure_eprom` (`eprom.cpp:41-77`) — where Phase 141 will call `eprom_params_for()`. Phase 140
  leaves it untouched but must not design an accessor that phase cannot use from here.
- `platformio.ini` — the fifth env's `test_filter`, `build_flags` `-I`, `lib_deps` and
  `build_src_filter` entries (D-11). Positive allowlists: a suite is invisible until it appears.
- `firestarter_app`'s test suite — where the DB-half TABLE-05 gate lands (D-12).
- Phase 141's loop reads all six columns; Phase 142 replaces the `vpp_path` consumers; Phase 144
  reconciles the flash delta D-10 defers.

</code_context>

<specifics>
## Specific Ideas

- **The test to write against:** a stranger who reads gh#15, its posted correction, and this table —
  and nothing else — should be able to implement the loop correctly and know exactly which numbers
  are datasheet-backed and which are reasoned. Anything in the table or its citations that does not
  move that answer toward yes is decoration.
- **The `0x08` contradiction gets named, not smoothed.** Whichever way research resolves it, the
  phase record says plainly that `PROJECT.md`'s prose and its own throughput table disagreed, and
  which one won and why. Silently picking one and moving on is the failure mode.
- **`verify_mode` is where the 6.25 V ceiling becomes concrete rather than rhetorical.** The
  datasheets' verify-at-raised-VCC step is unreachable on this shield; the citation for that column
  is the place to say so in the same file as the number, not only in Phase 146's ledger.
- **`energy_cap_us` on `0x0B` is reasoned, not derived — and must be labelled that way.** Milestone
  D-02 is explicit that minipro never runs the algorithm, so the 50 ms figure comes from
  `100 × 500 µs` being the classic 2716 total programming time, not from a wire observation. gh#15's
  posted comment already asked the community to correct it; the citation must match that framing.
- **Expect Phase 140's AVR flash delta to be ~0 and say so before measuring it.** A ~0 delta from a
  garbage-collected table looks identical to "we forgot to add the table". Stating the prediction
  first is what makes the measurement evidence.

</specifics>

<deferred>
## Deferred Ideas

- **Wiring the table into `eprom.cpp`** — Phase 141 (the loop) and Phase 142 (the VPP branch at
  `:145`/`:218`). D-10 keeps this phase's `eprom.cpp` byte-unchanged.
- **Removing `program_mismatched_bytes()` / `verify_and_update_mask()` / `NUMBER_OF_RETRIES` / the
  adaptive growth formula** — LOOP-02, Phase 141.
- **The 32-bit-safe delay helper** — LOOP-07, Phase 141. C3's real purpose; the 75 ms overprogram
  pulse D-08 caps is what needs it.
- **`--pulse-us` bounds and pre-validation** — HOST-01…05, Phase 143. D-07's `max_pulses` backstop
  exists partly to survive it, but the flag itself is not this phase's.
- **Re-baselining `native_trace_v131` and reconciling the flash/RAM delta** — TEST-06 / TEST-08,
  Phase 144.
- **A possible `0x08` family split** (if research finds the 32-pin row genuinely spans Intelligent
  and Quick-Pulse silicon) — recorded as a finding for Phase 146, never forced into a wrong single
  value here (D-06).
- **Fixing F-138-05** (`check_size_baseline.py`'s uncaught KeyError on an unknown native env) —
  inherited, accepted, not fixed. Owner `henols`.

### Reviewed Todos (not folded)

- **"Skip VPP error/warning checks when VPP is unused (reads/blank-checks)"**
  (`2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md`, score 0.9) —
  reviewed, not folded (operator decision, this discussion). A genuine VPP-routing behavior change:
  Phase 142 (VPP-01…04) territory. `139-CONTEXT.md` already reviewed and deferred it there. Folding
  it here would put a behavior change in a phase that decided to leave `eprom.cpp` byte-unchanged.
- **"FM1608 byte 0 write never lands — register cache-skip elides all three shift-register strobes"**
  (`fm1608-byte0-write-never-lands-register-cache-elision.md`, score 0.9) — reviewed, not folded. A
  real firmware write-path defect, but on an NVRAM part outside the three 27C protocols this
  milestone scopes, and its fix lives in the register-cache layer, not the EPROM algorithm.
- **"CONFIG_VERSION is not bumped when a calibration default changes"**
  (`config-version-not-bumped-strands-stale-eeprom-calibration.md`, score 0.7) — keyword match on
  "firmware"/"vpp"; unrelated to the parameter table.
- **"AT28C256 write-path failure (gh#20)"** (`at28c256-write-path-failure-gh20.md`, score 0.6) —
  protocol `0x0D`, a different family and a different milestone's problem.
- **"avrdude MCU-detection fallback"** / **"Fix JP4 labels + Rev-2 revision block"** (both score
  0.6) — matched on bare words ("fallback", "chip", "database"); neither touches this phase.

</deferred>

---

*Phase: 140-Parameter Table*
*Context gathered: 2026-08-09*
