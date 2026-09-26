# 146-CORRECTIONS.md — Consolidated Correction Register

Phase 146 / CLOSE-04's discharge of the inherited correction queue (D-04, D-05). Per D-14, this
register never reproduces a false statement's exact wording where that wording itself carries a
forbidden phrase; the false-text column cites `file:line` instead. This file is a **register**, not a
ledger and not a fix: see the three non-claims at the close.

## Register

| Row | Origin finding | Owning `file:line` | False text (cited, not quoted where it would trip D-14) | Corrected text | Owning plan |
|---|---|---|---|---|---|
| C-1 | 143 D-01 (sequencing-spine sentence) | `.planning/ROADMAP.md:167` | The spine sentence asserted Phase 143 (HOST) is "independent of Phases 140–142 (different repo)" and can run in parallel with them. | Phase 143 is dual-repo; 140/141/142 are landed prerequisites, not parallel peers — HOST-02's progress mechanism is firmware-side (`firestarter/src/proms/eprom.cpp:430`) and HOST-01's budget is computed from Phase 140's table (`firestarter/include/eprom_budget.h:27,52`). | 146-05 (verified landed at `8df5e564`; not re-landed) |
| C-2 | 143 D-01 (dependency line) | `.planning/ROADMAP.md:382` (measured `:380` at research time; the C-1 block above inserted two lines first — both readings recorded, neither preferred) | The Phase 143 charter's dependency line read "Independent of Phases 140–142 (different repo)". | Phase 143 depends on Phase 140 and Phase 141 as landed prerequisites and is dual-repo; the convergence-at-Phase-144 half of the original line is correct and stands. | 146-05 (verified landed at `8df5e564`; not re-landed) |
| C-3 | C3 / 141 H3 | `.planning/PROJECT.md:155` (original C3 row); mechanism at `firestarter/src/json_parser.c:466-469,304-306` and `firestarter/include/firestarter.h:197` | The C3 row's "with C1 applied, no *pulse* comes near it" reads as true of the whole wire, not only of `chip_database.json` data. | The `pulse-delay` wire field is parsed unclamped into a `uint32_t`; an over-ceiling value is reachable on the wire regardless of the host's own bound, and is now **delivered** (not truncated) via Phase 141's split-delay helper (`firestarter/src/proms/memory.cpp:310-323`); the only firmware-side refusal is `0x0B`'s pre-flight check (`eprom.cpp:90-110`), inert on `0x07`/`0x08` because those rows ship `energy_cap_us == 0`. Recorded, not clamped (D-06) — Backlog **999.31** owns the adjacent decision of whether to add a bound. | 146-05 (block landed in `PROJECT.md` this plan) |
| C-4 | 141 H4 | `.planning/phases/141-per-byte-program-loop/141-CONTEXT.md` (its own D-01 figure, cited by location, not by numeral per D-14's citation discipline — `141-LOOP-RECORD.md` §12 H4 already declined to restate it) | An inherited larger figure for the `0x0B` worst-case accumulated-energy overshoot. | The re-derived worst case is exactly **99998 µs** (two pulses at `w = 49999`), not 99999 and not the larger inherited figure; already correctly derived in `firestarter/CLAUDE.md`'s `0x0B` row (line 66). No `.planning` block is written for this row: the false site is a closed phase's own context document, which per this register's block-versus-history rule (§3 below) gets a row only. | 146-05 (register only — no editable live site) |
| C-5 | F-140-05 | `.planning/PROJECT.md:212` **and** `:213` (two rows, not the one CONTEXT names); `:214` conflates a third cell | The `0x07` **and** `0x08` throughput-table rows both showed an `overpulse` column of `3 × N × pulse`; the `0x0B` row's `max pulses` cell read "50 ms energy cap". | The shipped table sets `overprogram_factor = 0` on **both** `0x07` and `0x08` (`firestarter/src/proms/eprom_params.cpp:45-49`) — the shipped source names this contradiction in its own comment at `eprom_params.cpp:41-43`. Both rows' worst-case figures were computed *with* the overpulse and so err conservatively. The `0x0B` max-pulses cell now reads the shipped value, **255** (`eprom_params.cpp:48`). The conditional prose above the table (`overprogram_factor > 0` gating) was already correct and needed no correction. | 146-05 (block landed in `PROJECT.md` this plan) |
| C-6 | F-140-07 | Public: gh#15 comment `#5233463320` line 39 (owed, not yet posted). Planning: `.planning/REQUIREMENTS.md:20` (D-02 rationale cell) and `.planning/PROJECT.md:176-181` (target-features bullet). History (recorded only, not edited): `.planning/PROJECT.md:1187` (dated footer) and `.planning/STATE.md:67`. | The published justification for `0x0B`'s `energy_cap_us = 50000UL`: "`100 × 500 µs` is exactly the classic 2716 total programming time." | The TI TMS 2516 datasheet's own total programming time for all bits is **100 seconds** (`.planning/phases/140-parameter-table/140-PARAM-TABLE-RECORD.md:259`); 50 ms is that same datasheet's *per-location* pulse width (`t_w(PR)` TYP), not a total. The value (50000 µs) keeps its genuine primary-datasheet basis; only the reason was wrong. `firestarter/doc/PROTOCOLS.md` §1.5 (lines 213-217) already carries this exact correction in place, landed by the Phase 140 record (plan 140-06) — not redone here. | 146-05 (both live `.planning` blocks landed this plan); public half owed by **146-12**; the two history sites are row-only per §3 |
| C-7 | F-141-07 | `firestarter/tools/catalog/messages.toml:922-924` (`DBG_PULSE_DELAY_MISMATCH`, id `0x15`) and `:163-167` (`MSG_INFO_RETRIES`, id `0x51`, orphan, record only) | `DBG_PULSE_DELAY_MISMATCH`'s format string reads "Mismatch, retrying with increased pulse delay from %d to %d" — describing the pre-Phase-141 adaptive-width-growth loop. | The per-byte loop landed in Phase 141 never increases pulse delay; every pulse is fixed-width. Both catalog ids are unreferenced by firmware (`141-LOOP-RECORD.md` §6, zero call sites) and are deliberately left assigned and unedited — no orphan-id gate exists and deleting an id risks a later reuse collision. Wording fix, not behaviour. | **146-07** (not landed by this plan; recorded here per D-05) |
| C-8 | F-144-01 | `firestarter/CLAUDE.md:277-279` | "`[env:native_loop_v131]` now runs **two** suites — the pre-existing `test_loop_eprom_v131` (**39 cases**) plus … **71 cases total**." | Measured truth (`.planning/phases/144-tests-build-verification/144-TEST-RECORD.md:139,145`): `test_loop_eprom_v131` is **47** cases, total is **79** cases (47 + 32). Two numerals are stale: `39` → `47`, `71` → `79`. `PROJECT.md:82`'s `71/71` figure is a separate, correct-when-written historical record and is not part of this correction. | **146-06** (not landed by this plan; recorded here per D-05) |
| C-9 (OD-B) | Surfaced, not decided, by `146-RESEARCH.md` §"(5)" | `.planning/PROJECT.md:216` | "Faster than today in the typical case — the current code can make 20 full block passes." | This milestone claims fidelity, not improvement (145 D-08); no control run of the pre-change loop exists in this milestone's evidence (`145-BENCH-LOG.md`'s "Boundaries" §1, `:2701-2707`). The comparative claim is corrected in place as scoping-era intent prose; the historical write-time figure that could read as a baseline is a recorded historical number cited to `145-BENCH-LOG.md:2702`, deliberately not restated by numeral here. | 146-05 (block landed in `PROJECT.md` this plan) |
| C-10 | Record-gate flip | `.planning/STATE.md:11` (removed, no longer present) | The Phase 130 record-gate RED asserted the ARM toolchain was **absent** from this devcontainer. | `146-03` measured the ARM toolchain **installable** in the devcontainer (with a two-package newlib delta CI omits). The sentence asserting absence was removed from `STATE.md` line 11 at commit `91a06604`, an interrupted `146-05` executor's own commit, closing the gate to rc=0. | 146-05 (already committed at `91a06604`; verified, not re-landed, by this plan's Task 1) |

## Divergences

Three findings in the inherited correction queue diverge from how `146-CONTEXT.md` / the replan brief
stated them. Per this phase's standing rule, where two readings exist, both are recorded rather than
one being silently preferred.

1. **The independence clause has no `PROJECT.md` false-statement site.** `146-CONTEXT.md`'s D-04 implied
   a `PROJECT.md` half of the roadmap-independence correction existed to be blocked. Re-measured this
   plan (Task 2): `grep -c "Independent of Phases 140"` against `.planning/PROJECT.md` returns **0**.
   `PROJECT.md:131` (and the dated footer at `:1183`) instead carry a true routing note — that the
   ROADMAP-prose correction is *owned by* Phase 146 / CLOSE-04 — which this plan updated from
   forward-looking ("deferred to") to discharged ("DISCHARGED AT Phase 146, plan 146-05"), not
   corrected, because it was never false. No block was manufactured to satisfy a premise research
   disproved.
2. **F-140-05's throughput-table correction spans two rows, not one.** The inherited framing named only
   the `0x07` row's false `overpulse` implication. Re-measured against `firestarter/src/proms/eprom_params.cpp:41-43`,
   the shipped source's own comment names the `0x08` row as carrying the identical contradiction. Row
   **C-5** above corrects both.
3. **F-140-07's energy-cap justification was already corrected in place** in `firestarter/doc/PROTOCOLS.md`
   §1.5 (lines 213-217) by the Phase 140 record (plan 140-06), before this phase ran. Row **C-6**
   discharges the remaining `.planning`-side sites; it does not re-edit the firmware document.

## Record gate

The Phase 130 record-gate RED at `.planning/STATE.md:11` is closed. Task 1 of this plan measured the
causation rather than inheriting it: the needle (`arm-none-eabi-gcc` and `absent` co-occurring on one
line) sits on line 11 at `d2c212f1`, `083e4e5f`, and every `146-04` commit through its last (`0accb44e`),
and is absent from line 11 starting at `91a06604` — an **interrupted `146-05` executor's own commit**,
whose message records the flip (`rc=1 -> rc=0`, `unlabeled 1 -> 0`). `146-04-SUMMARY.md` reports the
gate as still RED; that report is **accurate at every `146-04` commit** — the RED did not close until
`91a06604`, which is not a `146-04` commit. So `146-04`'s report is not an under-claim. The divergence on
record is the replan brief's first-version §4, which credited `146-04` with the flip; that attribution
was wrong and is corrected by this row rather than by editing the replan brief (a dated planning
artifact — history, row only). Both readings (the brief's original attribution and this plan's
re-measured one) are stated here side by side rather than one being silently preferred.

## Block versus history

**The rule:** live prose that a future milestone's scoping pass will read *in situ* gets a labelled
`⚠ CORRECTION` block, appended immediately after the text it corrects, because that is what warns the
next reader on the spot. Prose that is already history — a dated footer, a decision-log entry, a closed
phase's own context or record document, `.planning/STATE.md` (edited by hand only, per this plan's own
constraints) — gets a register row here and nothing else, because history is not edited; editing it
would misrepresent what was known and said at the time.

**Sites that got a block (this plan):**
- `.planning/PROJECT.md:131` — updated from forward-looking to discharged (true statement, not a
  correction; see Divergence 1).
- `.planning/PROJECT.md`, after the wire-field C3 row (row **C-3**).
- `.planning/PROJECT.md`, after the throughput table (row **C-5**).
- `.planning/PROJECT.md`, after the energy-budget bullet (row **C-6**).
- `.planning/PROJECT.md`, after the "Faster than today" sentence (row **C-9**).
- `.planning/REQUIREMENTS.md`, after the D-02 scoping table (row **C-6**, requirements half).
- `.planning/ROADMAP.md:169` and `:396` — landed by the interrupted executor at `8df5e564` (rows
  **C-1**/**C-2**); this plan verified, did not re-land.

**Sites that got a row only (row-only list, this register):**
- `.planning/PROJECT.md:1187` — dated v1.31-start footer (row C-6).
- `.planning/STATE.md:67` — row C-6; and `.planning/STATE.md:11` — row C-10 (the record-gate sentence
  itself was removed by a prior commit, not edited by this plan).
- `.planning/phases/141-per-byte-program-loop/141-CONTEXT.md`'s D-01 figure — a closed phase's own
  decision-context document (row C-4).
- The replan brief's §4 misattribution — a dated planning artifact, not a live-record site (Record
  gate section above).

## Adjacency

Two findings sit in the exact lines the owed `--pulse-us` documentation entry must be inserted into in
`firestarter_app/README.md`'s `write` options list (`:316-318`), so both are in scope by adjacency even
though neither is one of CLOSE-03's five named topics. Both land in plan **146-07**, not this plan.

| Row | Site | False text | Shipped surface (measured) | Owning plan |
|---|---|---|---|---|
| **A-1** | `firestarter_app/README.md:316` | `-b`'s long name is documented as `--ignore-blank-check`. | The shipped long name is `--no-blank-check` (`firestarter_app/firestarter/cli_handlers.py:551`). | 146-07 |
| **A-2** | `firestarter_app/README.md:316` | `-b` is documented as also skipping erase. | Skipping erase is now a **separate** flag, `--skip-erase` (`cli_handlers.py:559-566`), whose own help text carries a warning that skipping erase on a non-blank electrically-erasable chip leaves un-erased bits that cannot be reprogrammed; `-b` alone is blank-check only. | 146-07 |

A documentation correction sitting inside the wording-only boundary this milestone holds to (no
behaviour change, no wire change) is why both rows are in scope here rather than deferred further.

## Non-claims

This register does not fix the unclamped wire field (row C-3) — that is Backlog **999.31**'s decision to
make, not this phase's.

This register edits no archived milestone document and no dated footer — every history site above is a
row, never a block (see "Block versus history").

This register is **not** the honesty ledger (`146-LEDGER.md`) — it is the correction-queue discharge
D-04/D-05 require; the ledger's job (permitted claims paired with explicit non-claims across the
6.25 V ceiling and the bench boundary) is separate and is not restated here.

## Claim-gate self-check

Run against this file alone in positional-argument mode:

```
$ python3 146-check-claims.py 146-CORRECTIONS.md
```

Expected: exit **0**, `PASS:` line naming this file, no missing-caveat complaint — `146-CORRECTIONS.md`
maps to the empty caveat set in `146-check-claims.py`'s `_CAVEAT_RULES` (D-11), so no 6.25 V paragraph
was pasted in here to satisfy a rule that does not apply to this file.

**Negative control (locator-can-fail proof):** a scratch copy of this file, outside this phase
directory, with one probed forbidden phrase appended, was run through the same gate and exited
non-zero, naming the planted label; the copy was discarded immediately after.
