# v1.31 Honesty Ledger — 27C Programming-Algorithm Fidelity

**Milestone:** v1.31 — 27C Programming-Algorithm Fidelity
**Phases:** 138 (Preconditions & Baseline), 139 (gh#15 Correction, outward), 140 (Parameter Table),
141 (Per-Byte Program Loop), 142 (High-Voltage Routing), 143 (Host Timeout, Progress & Pulse Override),
144 (Tests & Build Verification), 145 (Bench Validation), 146 (Close — Honesty Ledger, Claim Gate &
gh#15 Reconciliation — this phase).
**Repository scope: dual-repo firmware-touching milestone.** `firestarter` (Arduino/AVR + a new
PY32F071 ARM CMake target) and `firestarter_app` (the Python host CLI) both carry v1.31 code; this
phase (`146`) is docs-and-claims only in `meta` and touches neither sub-repo (D-06).

**Firmware submodule (`firestarter`) HEAD:** `f8ac6439728fdb44665db38bc7e6d26b15fcda06` (`f8ac643`) —
captured live via `git -C /workspaces/firestarter rev-parse HEAD` at this plan's own execution
(2026-08-17), **measured here, never reused from a prior document's citation.** (`146-ARM-BUILD-RECORD.md`'s
own capture, `fa6c9c7`, is four commits earlier — plans `146-04` through `146-07` landed in between; both
readings are correct for the moment each was taken.)
**Host submodule (`firestarter_app`) HEAD:** `3cf429f52ad5f693076d309fc016e25f257d85cb` (`3cf429f`) —
captured live via `git -C /workspaces/firestarter_app rev-parse HEAD`, same session, same discipline.
**Meta HEAD (this repository, immediately before this plan's own commits):**
`825ead7c78367eef38568d9757897698946aba0b`, branch `gsd/v1.31-27c-programming-algorithm-fidelity`.

**Oracle:** software- and one-part-bench-only — five gates/suites, each named with its own count,
re-confirmed live this plan except where a build would be required and is not (D-06):

1. **This phase's own claim gate**, `146-check-claims.py`, armed at **five** `_HERE`-built targets:
   run with no argument this session it returns **rc=1**, naming the **three** artifacts not yet on
   disk (`146-GH15-RECONCILIATION.md`, `146-RELEASE-NOTES-fw.md`, `146-RELEASE-NOTES-app.md` —
   `146-09`/`146-10` own them); run positionally against this file alone it is recorded **rc=0** at the
   end of each task below.
2. **Its fixture suite**, `test_check_claims_v131.py`: **14 passed, 1 failed**, re-run live this plan
   (`python3 -m pytest test_check_claims_v131.py -q -o addopts=""`). The one failure is
   `test_armed_against_the_five_real_closing_artifacts`, RED by construction until `146-11` — its own
   assertion message says so.
3. **The CLOSE-03 documentation checker**, `146-check-close03-docs.py`: **rc=0**, 4 targets
   (`firestarter/doc/PROTOCOLS.md`, `firestarter/CLAUDE.md`, `firestarter/README.md`,
   `firestarter_app/README.md`), zero forbidden-phrase matches, re-run live this plan.
4. **The Phase 130 record gate**, `check_record_corrections.py`: **rc=0**, tally
   `{'block': 23, 'line-label': 4, 'inline-history': 6, 'inline-allow': 10, 'superseded': 12}`,
   re-run live this plan.
5. **Both sub-repo suites**, cited rather than re-run (D-06 forbids a build this plan does not need):
   `firestarter`'s native suite **314 passed** and `firestarter_app`'s host suite **1590 passed** (1
   warning, 30 snapshots passed) — both recorded in `146-06-SUMMARY.md`/`146-07-SUMMARY.md` immediately
   after committing, not re-derived here.

**Plus one hardware fact and one CI fact, stated once here because they bound everything above them:**
the PY32F071 ARM target was compiled **once, locally**, at firmware commit `fa6c9c7`, emitting exactly
one `firestarter_py32f071.hex` (78769 B) — a **delta** against a target no CI run has ever compiled
against any v1.31 code, explicitly **not** CI parity (`146-ARM-BUILD-RECORD.md` §3); and **neither
repository's CI has run against any v1.31 code beyond Phase 138** — the firmware's remote milestone tip
is Phase 138's own last commit and the host's remote tip is the branch point itself
(`146-ARM-BUILD-RECORD.md` §1). Zero pushes, zero workflow dispatches, this phase included (D-01).

**Generated:** 2026-08-17, plan `146-08`.

**Composes with (cross-reference only — no data copied):**
- `.planning/REQUIREMENTS.md` §"Evidence ceiling" — the permitted/not-permitted wording this ledger
  distils into evidence tiers and claim classes, reproduced verbatim below.
- `.planning/STATE.md:2043` (meta commit `d02a88a0`) — the MERGE-05 +96 B adjudication, quoted verbatim
  below rather than re-derived.
- `.planning/phases/145-bench-validation/145-BENCH-LOG.md` — the nine numbered boundaries, the "Not
  measured" and "Carry-forward hand-offs" sections, and the four-criterion phase verdict.
- `.planning/phases/145-bench-validation/145-08-SUMMARY.md` — the closing prose's own carry-forward
  count, one of the three readings this ledger states rather than silently prefers.
- `.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-CORRECTIONS.md` — the
  full correction register; this ledger points at it for mechanism corrections rather than duplicating
  its rows.
- `.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-ARM-BUILD-RECORD.md` —
  the ARM build observation and its mandatory delta-not-CI-parity caveat.
- `.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-CITATIONS.md` §§0.1,
  0.4, 0.5, 0.6 — the D-01 no-push oracle, the tracked-gitlink delta, the gh#15 read-only state, and the
  Phase 130 record-gate baseline.
- `.planning/phases/144-tests-build-verification/144-TEST-RECORD.md` — the requirement-to-evidence map,
  the suite/env count table, the findings register and the hand-offs this ledger reports on.
- `.planning/phases/141-per-byte-program-loop/141-LOOP-RECORD.md` — the MERGE-05 verdict, the findings
  register, and the two hand-offs this phase discharges as corrections.
- `.planning/phases/143-host-timeout-progress-pulse-override/143-HOST-RECORD.md` — the honest headline,
  the padding rule, and the non-claims this ledger's claim table draws its host-side rows from.
- `.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-06-SUMMARY.md` and
  `146-07-SUMMARY.md` — the post-commit suite baselines cited in the Oracle line above.
- `.planning/ROADMAP.md` §"Phase 999.30" and §"Phase 999.31" — the two carry-forwards already filed as
  backlog stubs, named rather than re-filed in the negative-space section below.
- **Every document above is referenced and verified here, never edited.** `git status --porcelain` on
  each of the ten paths above (the two `145-` files, `146-CORRECTIONS.md`, `146-ARM-BUILD-RECORD.md`,
  `146-CITATIONS.md`, `144-TEST-RECORD.md`, `141-LOOP-RECORD.md`, `143-HOST-RECORD.md`, and both
  `146-0{6,7}-SUMMARY.md` files) is confirmed **empty** at this plan's execution, re-checked again
  immediately before the Task 3 commit below.

---

## Status / claim key

Reused from `122-LEDGER.md` / `137-LEDGER.md`, unchanged:

- **`PERMITTED`** — a wording backed by a measured, re-runnable software artifact (a test, a source
  scan, a size report, a live re-derivation) or, where named, a single-part bench result with its scope
  stated.
- **`CONTEXT-ONLY`** — measured and cited for context, but explicitly not a gate.
- **`FORBIDDEN`** — the ceiling's forbidden claim shape. Appears in this ledger only as a citation of
  what is *not* claimed, never as prose asserting it.

---

## The ceiling, then the asymmetric coverage

### The ceiling

Quoted verbatim from `.planning/REQUIREMENTS.md` §"Evidence ceiling — fixed before any code moves"
(`:41-51`), including the not-behavior-preserving clause, so no downstream reader — `146-09`'s
reconciliation, `146-10`'s two release bodies — has to re-derive it:

> The ~**6.25 V program-VCC** all four vendor algorithms assume for threshold margin is **unreachable
> on this shield** — the RURP has no VCC-raise path. This milestone buys *timing / pulse-count / verify*
> fidelity and **not** silicon-margin fidelity. It is hardware-bound, best-effort, the same shape as
> prior hardware-bound graduations. **gh#15 omits this entirely**, so its acceptance criteria imply a
> fidelity unreachable on this hardware and are amended by CLOSE-04.
>
> This change is **not behavior-preserving**: it changes *how* bytes get programmed. Golden traces and
> bench-verified write results encoding today's pulse cadence will legitimately shift. Re-baselining is
> expected work, not a regression.

**Consequence, in this ledger's own words:** this milestone buys timing, pulse-count and verify fidelity
and **not** silicon-margin fidelity. The debt is hardware-bound — no shield revision this project has
ever built carries a VCC-raise path — and it is tracked as a named future requirement, **FUT-VCC**, in
`.planning/REQUIREMENTS.md` §"Future Requirements". gh#15 omits the ceiling entirely, which is exactly
why its acceptance criteria imply a fidelity this hardware cannot reach and why `146-09`'s reconciliation
must amend them rather than answer them as filed.

**The MERGE-05 flash-band adjudication, quoted verbatim** from `.planning/STATE.md:2043` (meta commit
`d02a88a0`, *"docs(145): record the MERGE-05 +96 B adjudication for Phase 146's honesty ledger"*),
compared character-for-character against the live file at extraction time (`sed -n '2043p'
.planning/STATE.md` against the block reproduced below — zero byte difference):

> "v1.31 ships +96 B of AVR flash over the v1.23-era MERGE-05 band on all three AVR targets (uno
> 24824→24920, uno328pb 24874→24970, leonardo 26906→27002; RAM unchanged at 1573/1579/2014), admitted
> under a named, SHA-attributed defect-fix exemption — `MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96`,
> firmware commits `eb563d2` (assert the program-voltage route around every program pulse) and
> `ebe9cb3` (raise the VPP settles to 1000us/100us on bench evidence) — rather than by moving the
> BASE-01 anchor or widening the band literal. The bytes are `eprom_internal_program_pulse()` plus its
> two VPP settle constants: a defect fix restoring behaviour the pre-v1.31 firmware had, not new feature
> surface. Leonardo ships at 27002/28672 B, 94.2% full, 1670 B free."

**Three facts that same STATE.md entry states three ways, named explicitly so a reader does not have to
infer them:** (1) a named, commit-attributed exemption constant —
`MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96` in `firestarter/scripts/check_size_baseline.py`, firmware
commit `fa6c9c7`; (2) a decomposed pass/fail string that keeps the growth visible rather than
laundering it into a moved anchor — `+96<=96=band0+exempt96` for leonardo, `allowance of 160 B (band
64 B + defect-fix exemption 96 B)` for the uno-class targets; (3) a negative control one byte past the
exemption — `test_policy_merge05_admits_the_documented_defect_fix` pairs the admission with a planted
+97 B leonardo case that exits 1.

**Two facts a reader would otherwise have to infer, stated here instead:** the finding this exemption
admits was **never remediated** — the +96 B was not reduced, shrunk or micro-optimised away, it was
named and let through; and Phase 144's earlier green on this same tripwire came from **the anchor
moving** to the v1.31 tip, not from growth staying inside the v1.23-era band (`size_baseline.json`'s own
`merge05_clause`, re-derived by `145-03` and stated there in exactly those terms). The two greens — 144's
anchor-move green and 145's exemption-admission green — are different mechanisms and neither is
restated as the other.

### The asymmetric coverage

**What was validated, and on what.** The required protocol, `0x07`, completed a full write→read→verify
cycle on real silicon — three distinct 64 KiB images on the Winbond W27C512, nine clean oracle cells
across both the firmware's own pass/fail and an independent host-side SHA compare. The evidence scope,
quoted verbatim from `145-BENCH-LOG.md`'s boundary 3 (`:2710-2714`):

> "The evidence scope is exactly one part, one controller, one shield revision: the Winbond **W27C512**,
> chip-id **`0xda08`**; controller **`leonardo`**; shield **Rev 2.0**, read off the silkscreen by the
> operator because the EEPROM `hw_revision` byte cannot distinguish 2.0 from 2.2 from the modified
> Rev 0. **Nothing here extrapolates to another protocol, another part, another board revision or
> another controller.**"

**The two skips, as dispositions, not gaps.** `0x08` (AM27C020) is `skipped-with-reason` — no part on
the bench this phase; its last known state is cited from Phase 99 (write #1 60 of 64 byte-exact, write
#2 at a different region 0 of 64, judged a **fail** under D-14's fixed taxonomy) and carried as **FUT-08**.
`0x0B` (M2716/M2732) is `skipped-with-reason` — neither part on the bench; its last known state is cited
from Phase 79 (22.4 V by operator DMM against 23.9 V by firmware at max pot, the strict ≥25 V bar
**not cleared**, then retired by operator override), with definitive proof parked at Phase 79 plan
`79-03` pending a physical chip. **Neither disposition is inferred from the `0x07` result** — `0x07`,
`0x08` and `0x0B` share a write path but not a part, a VPP path or a bench result, and Phase 145's own
record makes no transfer between them.

**A third deliberate non-spend.** A true-UV `0x07` data point — a TMS27C512 — was not taken. The part is
one-shot with no eraser on hand, and the algorithm under test is identical to the W27C512's, so an
irreversible part was judged not worth the data point this milestone. This is a decision (D-01 in
`145-BENCH-LOG.md`'s own numbering), not an obstruction, and it is still a reading this milestone does
not have. Carried forward as item 8 in the negative-space table below.

**Two load-bearing bench-posture facts.** No silicon-touching invocation in Gate 2 or Gate 3 used
`--force`, `--skip-erase` or `--no-blank-check` — corroborated at the wire level by `Flags set:
CanErase (0x02)` on every write. And D-09's single re-seat allowance was **not consumed**: the
2026-08-16 session-1 failure had a firmware cause and no chip was ever touched, so the allowance was
offered, declined for want of a named physical cause, and stands unspent — a refusal the later
firmware root-cause vindicated.

**Two-state taxonomy used throughout, never the bare unqualified claim word:** *validated* and
*skipped-with-reason*. Where this ledger needs to say something was not established, it says **not
established**, **not measured**, or **remains open** — never the word the phase's own claim gate
forbids unqualified, including in a hyphenated compound.

---

## Evidence tiers — weakest to strongest

This milestone's evidence is not one uniform thing measured to varying degrees of confidence — it is
**seven different kinds of evidence**, and grouping claims by tier (rather than one row per requirement
category) is what keeps a native-only count from reading as equivalent to a bench observation. **The
ordering rule, stated once:** each tier down this list rests on evidence of a different *kind*, not a
weaker amount of the same kind, than the tier above it — a native-simulated count is not partial credit
toward a bench measurement, and a source-contract pin is not partial credit toward a behavioural test.
Moving a claim up a tier requires new evidence of that tier's kind, never more confidence in the
evidence already held.

1. **Never run.** Neither repository's CI has executed against any v1.31 code beyond Phase 138 — the
   firmware's remote milestone tip is Phase 138's own last commit and the host's remote tip is the
   branch point itself (`146-ARM-BUILD-RECORD.md` §1). The ARM `py32f071` target's state, as `146-03`
   observed it, belongs here too: one local compile, carrying its **mandatory delta-not-CI-parity
   caveat** — it is "not CI parity: no CI run has been made or observed, the runner image is different,
   the package closure was not compared" (`146-ARM-BUILD-RECORD.md` §3).
2. **Structurally unreachable.** The 6.25 V program-VCC ceiling (no shield revision has a VCC-raise
   path); the program-window rail's behaviour under load (the held-rail DMM proxy is defeated by
   DTR-reset-on-close, a standing Phase-97 tooling gap); and intra-block progress delivery on the
   Uno-class controllers, where the emission is compiled out via `#ifndef SERIAL_ON_IO` rather than
   merely untested.
3. **Cited, not re-derived.** The two skipped protocols' last known states — `0x08` from Phase 99
   (write #1 60/64, write #2 0/64, judged a fail), `0x0B` from Phase 79 (22.4 V DMM against 23.9 V
   firmware, the ≥25 V bar not cleared) — and the historical pre-v1.31 write figure of **22.84 s**
   appearing in Gate 2's cycle-1 record, which `145-BENCH-LOG.md`'s own boundary 1 names explicitly as
   **a recorded historical number, not a control measurement** — not taken on this part, in this
   session, under these conditions.
4. **Source contract only.** The operation-level high-voltage disable guarantee (VPP-02: every exit from
   the write path disables every active route) is pinned by native tests against production code, not
   observed as a voltage on any rail; the `leonardo`-only progress-emission guard is pinned by a source
   scan (`tests/test_progress_emission_is_leonardo_only.py`) because the file implementing the Uno-class
   UART teardown compiles in **no** native environment and so cannot be exercised behaviourally
   (`143-HOST-RECORD.md` §5 item 3); and the CAP-03 advertised-budget byte layout is pinned by
   `tests/test_ack_layout_source_contract_v143.py`, never observed as bytes on a real wire capture.
5. **Native-simulated.** This milestone's own native environment counts, each stated with the fact that
   it runs in **no CI leg of either repository**: `native_params_v131` **9 cases / 1 suite**,
   `native_loop_v131`'s `test_loop_eprom_v131` **47 cases** (79 total with its companion suite — the
   corrected figure, `146-CORRECTIONS.md` row C-8), and `native_trace_v131`, RED by design because that
   fixture pins `millis()` to `AlwaysReturn(0)` and so structurally cannot record any of this milestone's
   time-gated emission (D-24). The pinned, CI-covered envs `native`/`native_nodevtools` hold unmoved at
   **141 cases / 17 suites** each.
6. **AVR-measured.** Per-target flash and RAM at this tip — `uno` 24920 B / 1573 B, `uno328pb` 24970 B /
   1579 B, `leonardo` 27002 B / 2014 B (94.2 % full, 1670 B free) — each carrying the admitted MERGE-05
   defect-fix exemption quoted verbatim above.
7. **Bench-measured on one part.** The validated `0x07` write-read-verify cycle (three 64 KiB images,
   nine clean oracle cells); the `--pulse-us` override exercised on silicon at 4688 µs against the
   database's own pulse; and the per-block progress claim that held on that same run (D-10 Claims A and
   B, 64 and 24 intra-block frames respectively, each independently corroborated).

---

## The four-column claim table

Reproduced with the prior ledgers' header, unchanged: class, permitted wording, evidence with its
measured source, and explicitly-does-not-prove. Every row's fourth cell is **non-empty** — that cell
**is** CLOSE-02's explicit non-claim, and a row without one would not satisfy the requirement.

| Class | Permitted wording | Evidence (measured, source) | Explicitly does NOT prove |
|---|---|---|---|
| **1. Parameter-table dispatch** `PERMITTED` | A single `const`, PROGMEM, `protocol_id`-keyed table (`0x07`/`0x08`/`0x0B`) carries `max_pulses`, `overprogram_factor`, `overprogram_cap_us`, `verify_mode` and `vpp_path` — no pulse-width column (pulse width is `handle->pulse_delay`), no new `chip_database.json` field, no second algorithm selector. | TABLE-01…05 (Phase 140); native tests TEST-01 (each protocol resolves to its own row); `eprom_params.h`/`eprom_params.cpp` read this plan, `sizeof(eprom_params_t) == 12` compile-time asserted on every target. | That any table value is itself the optimum figure a primary datasheet would settle on for every part in a family — `FUT-MAXPULSE` and `FUT-OVERPROG-MAP` both remain open, needing a per-part datasheet sweep this milestone did not do. |
| **2. Per-byte pulse-to-verify loop, as it ships** `PERMITTED` | Fixed-width pulses, verified after each one, no width growth between attempts (LOOP-01); already-matching and `0xFF` bytes are skipped without a pulse (LOOP-06). The bench-validated image contains a **defect fix to this same loop phase's own shipped code** — session 1's first-byte program failure (found on real silicon, not in a native test) was root-caused and fixed by a debug session (`eb563d2`, `ebe9cb3`) before Gate 2's three counted cycles ran. | LOOP-01…08 (Phase 141); TEST-02/05 (native); `145-BENCH-LOG.md` Gate 2 (nine clean oracle cells, three distinct 64 KiB images). | That this holds on any part, controller or shield revision beyond the one bench scope (W27C512 / `0xda08` / `leonardo` / Rev 2.0); that v1.31 programs faster or more reliably than what preceded it — this milestone claims fidelity, not improvement, and no pre-v1.31 control run was made (D-08). |
| **3. Hard-fail at budget, with address and pulse-count reporting** `PERMITTED` | A byte that does not verify within `max_pulses` aborts the block, disables every active high-voltage route, and reports the failing address plus its pulse count via `MSG_ERR_MAX_PULSES`. | LOOP-05 (Phase 141); TEST-04 (native); `eprom.cpp:467-468` read this plan. | That `0x07`/`0x08` have any **upper bound** on pulse width before this refusal is reached — both rows ship `energy_cap_us = 0` (uncapped), so `MSG_ERR_PULSE_TOO_WIDE` is unreachable on them; only the host's own `1..65535` range bounds a run (Backlog **999.31**). |
| **4. High-voltage routing consolidation and its exit asymmetry** `PERMITTED` | One set of routing masks is shared by `eprom_check_vpp()` and every write and error path (VPP-03); **every** exit — success, verify failure, max-pulse failure, error return — disables every active route (VPP-02). | VPP-01…04 (Phase 142); `142-VPP-RECORD.md` native tests against production code. | Anything about the *voltage actually present* at the socket under load on any run — that reading was never taken this milestone (blocked by DTR-reset-on-close); this class is about routing logic, not a measured rail. |
| **5. Host-side long-block survival and intra-block progress, controller-only** `PERMITTED`, with a load-bearing non-claim | A write whose block exceeds the previous 10 s transport timeout completes without a serial timeout (HOST-01); the user sees intra-block progress on a long write (HOST-02) — delivered on **`leonardo` only**, compiled out on `SERIAL_ON_IO` targets via `#ifndef SERIAL_ON_IO`, structurally, not by choice. | HOST-01/02 (Phase 143); `143-HOST-RECORD.md` §3 BF-1/BF-2, §5 non-claim 1. | Anything about `uno`/`uno328pb` intra-block progress — the emission does not exist there, not merely untested (structurally absent, `145-BENCH-LOG.md` "Not measured" item 14). |
| **6. Per-run pulse override, with its bound-provenance narrowed** `PERMITTED`, with an explicit non-claim | `firestarter write --pulse-us N` overrides the database pulse for that run, riding the existing wire field, refused outside `1..65535` before any serial byte is sent (HOST-04/05). | `143-HOST-RECORD.md` §2, §5 item 6; `145-BENCH-LOG.md` Gate 3 (30.94 s at `--pulse-us 4688` against 11.87 s at the database pulse for the same 4096 bytes, a 19.07 s gap against 18.79 s predicted). | That the `1..65535` bound is a wire-type constraint — it is **minipro parity only**; the wire's own `pulse-delay` field is parsed by `extract_long` into an **unclamped** `uint32_t` and a value above 65535 is reachable on the wire independently of this flag (`146-CORRECTIONS.md` row C-3; Backlog **999.31** owns the adjacent decision of whether to add a firmware-side bound). |
| **7. Test and build position** `PERMITTED` | `uno`, `uno328pb`, `leonardo` and `native` all build and pass; native env counts hold at `native`/`native_nodevtools` **141/17** each, `native_params_v131` **9/1**, `native_loop_v131` **47** cases (**79** total, corrected — `146-CORRECTIONS.md` row C-8); AVR sizes stand at `uno` 24920 B, `uno328pb` 24970 B, `leonardo` 27002 B, each carrying the MERGE-05 exemption quoted above. | TEST-01…08 (Phase 141/144); `144-TEST-RECORD.md` §2/§14; `146-ARM-BUILD-RECORD.md` §2 (cited, not re-measured, per D-06). | That any of `native_params_v131`, `native_loop_v131` or `native_trace_v131` runs in **any** CI leg of either repository — none does, ever, by name (`141-LOOP-RECORD.md` §10). |
| **8. The CI position** `PERMITTED`, with a load-bearing non-claim | Both sub-repo suites pass **locally** at measured counts: `firestarter` **314 passed**, `firestarter_app` **1590 passed** (1 warning, 30 snapshots passed) — re-confirmed after every commit this phase (`146-06-SUMMARY.md`, `146-07-SUMMARY.md`). | Suite runs cited above; `146-ARM-BUILD-RECORD.md` §1 (the CI-run measurement). | **No CI run has exercised any of this milestone's v1.31 code, on any target, AVR or ARM.** The most recent CI run on either repository's milestone branch predates Phase 140 by commit distance; "green locally" and "green in CI" are never compressed into one statement here. |
| **9. The database position** `PERMITTED` | No chip's `support_status` changed as a result of this milestone's bench runs; `chip_database.json` is byte-unchanged across the whole milestone. | BENCH-03 (D-07); `145-BENCH-LOG.md` Criterion 4 — re-confirmed at the tip: whole-milestone diff **zero bytes** (`4d18b645`→HEAD), generator-inputs diff **zero bytes**, AST write-locus checker **exit 0**, histogram **736 supported / 9 adapter-required / 1 protocol-not-implemented / 746 total**. | That this milestone graduated any chip, or changed any chip's evidence-gated status in either direction — none did, and none was attempted. |

Every byte, percentage and count figure in the table above is cited to the record that measured it at
this milestone's tip: TABLE-01…05 and `eprom_params.h`/`.cpp` for row 1; `145-BENCH-LOG.md` Gate 2 for
row 2; `eprom.cpp` and TEST-04 for row 3; `142-VPP-RECORD.md` for row 4; `143-HOST-RECORD.md` for rows
5-6; `144-TEST-RECORD.md`/`146-ARM-BUILD-RECORD.md` for row 7; `146-06/07-SUMMARY.md` for row 8;
`145-BENCH-LOG.md` Criterion 4 for row 9 — no figure above is carried from a record a later phase
superseded (the `native_loop_v131` **47/79** figure in row 7 is itself an example: it replaces
`firestarter/CLAUDE.md`'s stale **39/71**, corrected by `146-CORRECTIONS.md` row C-8, and this table
uses the corrected reading). **Re-confirmations, stated as such:** row 8's suite counts were re-measured
by this plan's own live run of `146-check-close03-docs.py` and `check_record_corrections.py` and agree
exactly with `146-06-SUMMARY.md`/`146-07-SUMMARY.md`'s recorded figures — a re-confirmation, not an
independent new count. **Where two readings exist, both are stated:** row 7's AVR sizes supersede the
93.8 %/1766 B Leonardo figures Phase 144 recorded, because the debug session's `ebe9cb3` (+96 B) landed
after Phase 144 closed — both figures are real for the moment each was taken, and `146-ARM-BUILD-RECORD.md`
§2 states the supersession explicitly rather than silently substituting the newer number.

---

## Mechanism corrections

Full register: `146-CORRECTIONS.md` (not duplicated here — its rows are the correction-queue discharge
D-04/D-05 require; this section names, in one line each, the four corrections that change what a reader
should believe about the *mechanism*):

- **The over-program factor the shipped table sets to zero, against a throughput table that implies
  otherwise on two rows.** `overprogram_factor = 0` on **both** `0x07` and `0x08` in the shipped
  `eprom_params.cpp` — the two `PROJECT.md` throughput rows that showed a `3 × N × pulse` overpulse
  column for those protocols were computed conservatively, not from the shipped value (`146-CORRECTIONS.md`
  row C-5).
- **The `0x0B` energy-cap value's primary-datasheet basis is real; its published reason was wrong.**
  `50000UL` keeps its genuine TI TMS 2716 datasheet basis (the per-location pulse width, not — as
  originally published — "100 × 500 µs, the classic 2716 total programming time," which is actually the
  datasheet's *total* figure, a different quantity) (`146-CORRECTIONS.md` row C-6).
- **The wire's `pulse-delay` field is parsed unclamped, delivered rather than truncated, and refused
  only on the row whose cap column is non-zero.** `extract_long` parses it into an unclamped `uint32_t`;
  Phase 141's split-delay helper **delivers** an over-ceiling value rather than truncating it; the only
  firmware-side refusal is `0x0B`'s pre-flight check, inert on `0x07`/`0x08` because those rows ship
  `energy_cap_us == 0`. **Explicitly: this field is recorded and not clamped.** Backlog **999.31** owns
  the adjacent decision of whether to add a bound (`146-CORRECTIONS.md` row C-3).
- **The shipped debug message described a deleted loop until this phase's wording change.**
  `DBG_PULSE_DELAY_MISMATCH`'s format string described the pre-Phase-141 adaptive-width-growth retry
  loop; the per-byte loop that shipped in Phase 141 never grows pulse width, so the message was corrected
  to describe a plain mismatch (`146-CORRECTIONS.md` row C-7, landed by plan `146-07`).

---

## Negative space — all twelve carry-forwards

Reproduced as twelve rows from the authoritative table at `145-BENCH-LOG.md:2522-2565` (its own header:
"Carry-forward hand-offs with no v1.31 owner (phase close)"), each carrying the item as that record
names it, the Owner text **verbatim** from its Owner column, where it lives now, and one line on what
was not established. **No backlog stub is filed and no state-file block is added for any of these**
(D-03): several already have a home in a named future requirement or an already-filed backlog item, and
the genuinely homeless ones are named here and nowhere else — which is the point of a ledger.

| # | Item | Owner (verbatim) | Home now | What was not established |
|---|---|---|---|---|
| 1 | A1's per-pulse overhead inside a multi-pulse retry loop (`0x0B` at `--pulse-us 200`, 250 pulses × 1024 bytes) | **no v1.31 owner** | None — genuinely open | No byte in either Gate 3 run needed more than one pulse; whether a genuinely-retrying regime's per-pulse overhead differs from the derived ~1436 µs upper bound is not established. |
| 2 | Verification-map row 27's literal claim ("operator confirms a smoothly moving bar, not an end-burst") | **no v1.31 owner** | None — genuinely open | The operator's four words ("It looked ok") contain neither discriminator; whether the bar moved smoothly or arrived as an end-burst is not established. |
| 3 | The MAIN write progress bar never reaching 100 % (new finding, `145-08`) | **no v1.31 owner** | Backlog **999.30** | The fix lives under `firestarter/` or `firestarter_app/` and D-16 forbade this phase from touching either; cosmetic/UX only, all six affected writes verified byte-exact, so no correctness claim is affected. |
| 4 | Program-window VPP (and internal VCC) under load | **no v1.31 owner** | None — genuinely open (carries `0x08`'s **FUT-08** droop hypothesis) | The Phase-97 DTR-reset-on-close tooling gap defeats the only proxy instrument; the rail's actual behaviour under load, on any protocol, is not established. |
| 5 | The root cause of the intermittent single-byte margin failure | **no v1.31 owner** | None — genuinely open | Mitigated by the shipped settle increase; ~17 clean cycles is not a root cause, and the cause itself remains open. |
| 6 | `0x08` (AM27C020) bench validation | **no v1.31 owner** | **FUT-08** | No part on the bench this milestone; its last known state (Phase 99: write #1 60/64, write #2 0/64) is a fail under D-14, not re-established here. |
| 7 | `0x0B` (M2716/M2732) bench validation | **Phase 79 plan `79-03`** — a real successor exists, parked, not a v1.31 owner | Phase 79 plan **`79-03`** | Neither part is on the bench; the graduation is parked pending a physical chip, and nothing in this milestone attempted it. |
| 8 | A true-UV `0x07` data point (TMS27C512) | **no v1.31 owner** | None — genuinely open | Reachable only by consuming an irreversible part with no eraser on hand (D-01); UV-specific `0x07` behaviour remains not established. |
| 9 | The 6.25 V program-VCC evidence ceiling | **the milestone's accepted debt — explicitly NOT this phase's to discharge** | **FUT-VCC** | Structurally unreachable on this shield. **This ledger is where the ceiling is *stated*, not where it is *discharged*** — the leading section above states it; nothing here resolves it. |
| 10 | MERGE-05's +96 B leonardo band breach — adjudication | **the operator, as a milestone requirements judgement** | **Discharged, not carried** | **Superseded by the adjudication recorded above** (`.planning/STATE.md:2043`, commit `d02a88a0`): the operator admitted the +96 B under a named, SHA-attributed defect-fix exemption rather than leaving it open. This row is listed for completeness against the authoritative table's own twelve, not because it is still open — see "The ceiling, then the asymmetric coverage" above for the quoted wording. |
| 11 | T-145-45 — a threat-register entry asserting a firmware mitigation that does not exist | **no v1.31 owner for the fix; Phase 146 may judge the wording** | None for the fix — filed as Backlog **999.31**'s documentation-defect note | `145-07-PLAN.md`'s register claims the firmware refuses over-cap pulses on `0x07`/`0x08`; `eprom.cpp`'s guard (`energy_cap_us > 0`) is inert on both rows, which ship `energy_cap_us = 0`. No fix is established; only the host's own bound protects a run today. |
| 12 | RQ-4's frames-per-block table | superseded, **no v1.31 owner** for a rewrite | None — genuinely open | It predicted zero intra-block frames at the database pulse; 64 were measured. Recorded as stale rather than cited as a passing prediction; nothing was retro-fitted to it. |

**Other named homes for undischarged findings across this milestone, distinct from the twelve bench
carry-forwards above:** `.planning/REQUIREMENTS.md` §"Future Requirements" also carries **FUT-PRESTO**
(true PRESTO margin verification for `0x08`, requiring a verify mode the RURP may not expose) and
**FUT-MAXPULSE** (per-part `max_pulses` from primary datasheets, open because Intel's 25-pulse figure is
confirmed but Microchip specifies 10) — neither is one of Phase 145's twelve bench carry-forwards, but
both are open items this milestone's own scoping never closed, named here per `146-CONTEXT.md` D-03's
instruction that "six of the remaining eight already have a home."

### Settling the counting disagreement — three readings, stated rather than reconciled

**The count is twelve.** That is what the authoritative table at `145-BENCH-LOG.md:2522-2565` has, and
what the Phase 145 verdict's own closing line says ("**Twelve items carry forward** with no v1.31
owner"). This ledger states twelve rather than any other number, above.

**A literal, live count of the Owner column's `no v1.31 owner` text against that same twelve-row table,
run for this ledger, returns NINE** — rows 1, 2, 3, 4, 5, 6, 8, 11 and 12 each carry the substring `no
v1.31 owner` somewhere in their Owner cell (rows 11 and 12 carry it as part of a longer phrase, "no
v1.31 owner for the fix" and "no v1.31 owner for a rewrite"). The remaining **three** rows name a real
owner instead: row 7 (**Phase 79 plan `79-03`**), row 9 (**the milestone's accepted debt**), and row 10
(**the operator**).

**Two other documents give different numbers, neither silently preferred over the other or over the
nine measured directly above:**

- `145-08-SUMMARY.md`'s own closing prose states **"12 carry-forwards, 10 of them with `no v1.31
  owner`"** (`145-08-SUMMARY.md:46`) — a number its own reproduced carry-forward table two sections
  later does not itself support: that table labels only **eight** rows with the exact phrase `no v1.31
  owner` and phrases row 11 differently ("none for the fix"), an internal inconsistency in that
  document that this ledger notes rather than resolves.
- `146-CONTEXT.md`'s D-03 arithmetic works from a count of **eight**: "No new backlog stubs and no
  STATE.md block for **the eight** `no v1.31 owner` items... two of the twelve are already filed
  (999.30, 999.31) and six of the remaining eight already have a home" (`146-CONTEXT.md:79-82`).

**All three readings — nine, ten, eight — are named here rather than reconciled into one.** The table's
twelve total rows is what this ledger states as the count of carry-forwards; the sub-count of how many
of those twelve carry the literal no-owner text is not settled by this ledger and is stated as all three
measurements found it.

---

## Process failures recorded here, not only technical ones

A ledger that admits only code defects is not an honesty ledger. Four process failures this milestone's
own record keeps visible:

1. **The correction queue: four phases each declined to make a correction they themselves found, and
   routed it forward in writing, discharged only at this phase's close.** Phase 140 found F-140-05 (the
   throughput table's stale overpulse implication) and F-140-07 (the energy-cap justification's wrong
   reason) and named both "Phase 146 / CLOSE-04's" rather than fixing them in place. Phase 141 found H3
   (the unclamped wire field) and H4 (the honest energy-cap worst case) and did the same. Phase 143 found
   its own roadmap-independence framing was wrong (D-01, §6) and routed it forward rather than editing
   `ROADMAP.md` itself. Phase 144 found F-144-01 (`firestarter/CLAUDE.md`'s stale native suite count) and
   handed it to Phase 146 / CLOSE-04 as well. All seven are discharged in `146-CORRECTIONS.md`, landed
   across plans `146-05`, `146-06` and `146-07` — none before this phase.
2. **Three inherited corrections did not hold as stated, found only because they were re-measured.**
   `146-CORRECTIONS.md`'s own "Divergences" section: (a) `146-CONTEXT.md`'s D-04 implied a `PROJECT.md`
   false-statement site for the independence clause that does not exist — re-measured, `grep -c
   "Independent of Phases 140"` against `PROJECT.md` returns **0**; the real site was a true routing
   note, updated from forward-looking to discharged rather than corrected as false. (b) F-140-05's
   throughput-table correction was framed as touching one row; re-measured against the shipped source's
   own comment, it spans **two** rows (`0x07` **and** `0x08`). (c) F-140-07's energy-cap justification was
   framed as needing a fix; re-measured, `firestarter/doc/PROTOCOLS.md` §1.5 already carried the
   correction, landed by Phase 140 itself before this phase ran.
3. **Acceptance locators in the prior phase were false GREENs — one passing against a record with no
   content in it.** Phase 145 found **three** acceptance locators that returned false GREENs this way
   (`146-CONTEXT.md:197`; the phase's own running total across all of Phase 145 reached **seven** broken
   acceptance locators, `145-09-SUMMARY.md:134`). This is why this phase's own claim gate carries **two**
   independent proofs of arming — the fixture suite (`test_check_claims_v131.py`) and a real-file
   plant-and-revert transcript (`146-CITATIONS.md` §3) — rather than trusting either alone.
4. **The tracked submodule pointers in the meta repository are stale for the whole milestone.**

   | Repo | Tracked gitlink (meta's `git ls-tree HEAD`) | Live HEAD (this plan, `git -C <repo> rev-parse HEAD`) |
   |---|---|---|
   | `firestarter` | `0933bd7d602efb30e4a666e8231ecf724e90ab09` | `f8ac6439728fdb44665db38bc7e6d26b15fcda06` |
   | `firestarter_app` | `cc036e8dc3cd77bbdfc7ec5190d79cdb172153c7` | `3cf429f52ad5f693076d309fc016e25f257d85cb` |

   Both gitlinks are v1.30-era tips, stale by the whole milestone and have been at every point in v1.31
   (`146-CITATIONS.md` §0.4). **Re-pinning is handed to `/gsd-complete-milestone`, not done here** — no
   criterion in this ledger, or anywhere else in this phase, asserts that the pointers match, because
   they do not and have not at any point this milestone.

---

## What no test, gate or review can close

At minimum:

- **The program-VCC ceiling.** 6.25 V is hardware, not firmware — no test in this or any future
  milestone answers it without a shield revision with a VCC-raise path, which does not exist.
- **The root cause of the intermittent single-byte margin failure.** Mitigated by a settle-time increase,
  not explained; ~17 clean cycles is not a root cause.
- **The program-window rail's behaviour under load.** The only available proxy — a held-rail DMM
  reading — is defeated by DTR-reset-on-close, a standing Phase-97 tooling gap this milestone did not
  fix.
- **Whether the two skipped protocols, `0x08` and `0x0B`, work at all on real silicon.** Both need parts
  nobody currently has on the bench.
- **Whether any of this matches what a datasheet specifies, in either direction.** `145-BENCH-LOG.md`'s
  boundary 2 (`:2707-2709`) states this limit in its own terms — cited by line range and paraphrased
  here, never quoted, because its own wording carries one of this phase's forbidden compounds: it says
  plainly that the 6.25 V ceiling's debt belongs to the milestone and that nothing in that record takes a
  position, one way or the other, on how faithfully the algorithm follows any datasheet.

**Scanner-status paragraph.** This ledger has been run, this plan, against: this phase's own claim gate
in positional mode against itself alone (**exit 0**, three times — end of each task); the same gate with
no argument against the default five-target set (**exit 1**, naming the three artifacts `146-09` and
`146-10` have not yet authored — expected at this wave, not a red); the gate's fixture suite,
`test_check_claims_v131.py` (**14 passed, 1 failed**, the one failure RED by construction until
`146-11`); the CLOSE-03 documentation checker (**exit 0**); and the Phase 130 record gate (**exit 0**).
**A green run of any of these gates means the forbidden vocabulary is absent from the scanned text and
the required caveats are present — it does NOT mean the prose is right.** That judgement is the
blocking operator wording review in plan `146-12`, which this ledger's own gate-runs do not substitute
for and must never be reported as discharging.
