# Research Questions

Open questions to resolve via deeper investigation. Appended by `/gsd-explore` and other workflows.

## Protocol-first architecture rebuild (v1.16) — added 2026-06-25

Source: `/gsd-explore` session 2026-06-25. See `seeds/protocol-first-architecture-rebuild.md`.

1. **Shared-primitive inventory.** What are the actual common operations across the current
   firmware handlers (`configure_eprom`, `configure_sram`, `configure_flash`, flash4, …)?
   Produce a decomposition: address setup, data strobe, poll/verify, VPP gate, page buffer,
   SDP unlock, chip-id. Which are genuinely shareable vs protocol-specific?
2. **Datasheet sourcing list.** Concrete list of datasheets to download: the 11 on-hand ICs +
   one representative common chip per minipro protocol bucket without silicon. Where are the
   authoritative copies?
3. **Current per-handler flash breakdown.** Measure today's Leonardo flash usage attributed
   per handler/family, to quantify where reuse buys the most headroom against the ~90% ceiling.
4. **protocol_id → name → datasheet map.** For every `protocol_id` in `chip_database.json`,
   the proper human name and the datasheet-verified behavior (write/erase algorithm, VPP,
   pin roles). This is the vocabulary the naming pass produces.
5. **Verification ledger format.** How to represent per-protocol bench status (PASS on
   Leonardo / `UNVERIFIED` / chip-needed) so it composes with the existing v1.13 per-family
   matrix + v1.15 EVIDENCE.{md,json} rather than replacing them.

## Community chip-validation command (dev test) — added 2026-07-02

Source: `/gsd-explore` session 2026-07-02. See `seeds/community-chip-validation-command.md`
and `notes/dev-test-design-decisions.md`.

1. **Health-proving write/verify pattern.** What data pattern does the write/verify step
   use? A fixed pattern (e.g. 0x00/0xFF/0xAA) is simple but blind to stuck/shorted address
   lines — a chip can pass while mis-addressing. An **address-derived pattern** (each byte a
   function of its address) makes verify catch address-line faults directly. This ties to the
   old Bug A "upper-address jitter" history — the exact failure class an address-derived
   pattern would surface. Decide before planning; also decide the UV small-region variant.

2. **Community PASS → support_status graduation.** Does a community-submitted PASS
   automatically graduate a chip's `support_status` (spec-only → supported), or only flag it
   for maintainer confirmation? Affects trust model: auto-graduation risks a bad bench
   config promoting a chip falsely; manual keeps the maintainer authoritative but adds
   triage load. How does the structured report reconcile/diff against the current DB entry
   inside `gsd-inbox`?

## Bus-config mask-model redesign — added 2026-07-02

Source: `/gsd-explore` session 2026-07-02. See `seeds/bus-config-clean-redesign.md`
and `notes/bus-config-mask-model.md`.

1. **Is the per-byte remap actually a measurable fraction of read/write time, or
   is it serial-bound?** The "faster" motivation for the bus-config redesign is a
   suspicion, not a measurement. At 250000 baud (~25 KB/s) a 512-byte read is
   ~20 ms of pure transport; the per-byte work in `mem_util_remap_address_bus`
   (the `rw_line`/`vpp_line`/`using_p1_as_vpp` branches + the address-permutation
   loop) may be negligible against that. Profile a real read AND write on both a
   straight-mapped chip (permutation loop skipped, `address_lines[0]==0xFF`) and a
   permuted chip. Decide whether perf can drive the redesign, or whether the
   generality goal must carry it alone. If marginal, an additive `static_low` +
   configure-time mask precompute may suffice instead of a breaking redesign.

## info jumper-display / 2516-family support — added 2026-07-02

Source: `/gsd-explore` session 2026-07-02. See `notes/info-jumper-display-design-audit.md`
and `seeds/rev22-3pin-header-2516-family-support.md`.

1. **Is TMS2532 VPP 25V or 21V?** The TI 2516/2532 datasheets specify 25V ±1V,
   but one web source (forum) claimed 21V for the TMS2532. Confirm against the
   primary TMS2532 datasheet before any voltage decision. The chip_database.json
   currently lists 2532 @ 25V (algorithm 0x0B).

2. **Can Firestarter actually PROGRAM a 2516/2532 today, or only read it?** The
   2516 is modeled on the same pinout key as an ordinary Intel 2716
   (`DIP24_2716`) and shares firmware algorithm `0x0B`. But datasheets show the TI
   25xx family takes the program strobe on **pin 20 (PD/PGM)** while Intel parts
   take it on **pin 18 (CE/PGM)**. Determine what pin firmware `0x0B` actually
   asserts the write-strobe on. If it strobes pin 18, a write to a 2516/2532 would
   fail (or corrupt) despite `support_status: supported` — meaning the 3-pin
   header on Rev 2.2/2.3 is what physically reroutes the strobe to pin 20, and
   Firestarter cannot program these parts on Rev 2.0/2.1 at all. Verify on-bench
   (operator owns Rev 2.2).

## 27C programming-algorithm fidelity — added 2026-07-02

Source: `/gsd-explore` session 2026-07-02. See
`seeds/27c-algorithm-fidelity-param-table-refactor.md`. Researcher confirmed the
firmware runs an iterative program→verify loop but diverges from every 27C
datasheet (escalating pulse instead of fixed 100µs; flat retry cap of 20 vs
per-part 10/25; no over-program margin; no 6.25V VCC). These items were
`[ASSUMED]` and must be verified before drafting the parameter table:

1. **Exact max-pulse count per part.** Intel's 25-pulse cap is confirmed for
   27C010 but assumed for 27C256/512; Microchip's count (~10) is assumed. Pull
   the per-part cap from each primary datasheet so the table's `max_pulses` rows
   are verified, not inherited.

2. **Which on-hand parts (if any) need the 3× over-program margin?** Only the
   older Intel "Intelligent" 27C algorithm applies an over-program pulse of 3×
   the pulses used; Quick-Pulse / Flashrite / PRESTO do NOT. Map each on-hand 27C
   part to its algorithm variant and decide whether the `overprogram_factor`
   column is ever non-zero for real inventory, or is purely forward-looking.

3. **Is a true fixed-100µs pulse achievable given the firmware's page-write pulse
   model?** Today the "pulse" is `CTRL_VPE_ENABLE` asserted/de-asserted around a
   whole page write (`eprom.cpp:115-125`), and width comes from `pulse_delay`.
   Confirm the timing granularity actually lets us hold 100µs per unit, or whether
   the page-oriented pulse shape needs rethinking to match the byte-level
   datasheet algorithm.

4. **Legacy NMOS 50ms path.** Confirm which parts currently mapped to 0x0B are
   the fixed-50ms-single-pulse NMOS parts vs. adaptive CMOS, so the "legacy" row
   is correct and we don't force a 50ms cadence onto a CMOS part that wants 100µs.

## White-box voltage calibration (v1.25) — added 2026-07-03

Source: `/gsd-explore` session 2026-07-03. See
`seeds/voltage-reading-whitebox-calibration.md` and
`notes/voltage-cal-design-decisions.md`. Resolve before scoping/planning:

1. **Is the bandgap really the dominant term?** Measure the true bandgap
   `V_bg = VCC_dmm × bandgap_adc / 1024` on 2–3 bench boards (Uno, Leonardo,
   uno328pb) and compare each to the hardcoded 1100 mV. Confirms Stage 1 carries
   the accuracy and quantifies the per-board spread (is it really ~±10 %?).
2. **Does the Stage-2 VPP fit show a real offset, or is it pure gain?** After
   applying the calibrated `V_bg`, measure VPP at 2+ pot levels and check whether
   the residual is a clean scale factor (one trim point suffices) or has an
   intercept (need two points). Decides how many Stage-2 points the wizard asks for.
3. **`CONFIG_VERSION` migration.** How to upgrade an existing user's stored EEPROM
   config to the new layout without silently mis-scaling readings — confirm the
   new bandgap field defaults to 1100 mV (identity) on migration and that the
   version-bump path is covered by existing config tests.
4. **Confirmation-read mechanism.** What's the cleanest way for firmware to return
   one raw `(bandgap_adc, voltage_adc)` sample on demand for the wizard — extend an
   existing `dev`/config command, or add a dedicated calibration command? Must not
   drive any rail as a side effect (safety).
5. **DMM/ground-truth tolerance.** What DMM accuracy do we assume, and should the
   wizard record the meter/measurement so a later re-cal can tell instrument error
   from real drift?

## Jumper display correctness (per pin map) — added 2026-07-10

Source: `/gsd-explore` session 2026-07-10. See `notes/jumper-display-ground-truth.md`
and seed `seeds/jumper-settings-per-pin-map.md`.

1. **Rev 2.x JP4 vs 32-pin pin-1-VPP chips.** JP4 routes VPP to "socket pin 1"
   (P1_VPP_JMP). On Rev 0/1 the 3-position JP3 selects between the 32-pin and
   28-pin seating of a chip's pin 1 — Rev 2.0/2.1/2.2 have only the single
   open/closed JP4. Does JP4 serve W27C010-class 32-pin pin-1-VPP chips as well
   as 28-pin ones, or only one seating? Does the Rev 2.3 3-pole 2x2 selector
   footprint restore the seating choice? Check Rev 2.x KiCad routing of
   `P1_VPP_ENABLE` relative to ZIF positions 1 vs 3.
2. **24-pin VPP chips (2716/2732/2532, 32 chips).** Protocol 0x0B applies VPE
   directly to the PGM pin, so no pin-1 routing should be needed and the
   current "no JP3/JP4 guidance" display is plausibly right — confirm against
   `rurp_schematics_rev1.pdf` (and Rev 2.x) that no jumper participates in the
   24-pin VPP path.
3. **`PROTOCOLS.md:136` wording.** It says 0x07-family VPP is applied "via JP4
   jumper routing", which contradicts pin-1-only JP4 routing for pin-22-VPP
   chips (DIP28_27512 → CTRL_VPP_VPE_DROP path). Establish the correct
   statement and fix the doc (lockstep with the meta-repo shield docs if §
   overlap).

## Dev-tools gating via release channel (999.15 / gh#8) — added 2026-07-28

Source: `/gsd-explore` session 2026-07-28. See `notes/dev-tools-gating-channel-split.md`
for the full design and the 999.15 stub rewrite in `ROADMAP.md`.

1. **What is the source-checkout override, and does it fail safe?** The design gates the
   host `dev` group off the package's own `__version__` (`firestarter_app/firestarter/__init__.py:1`;
   pre-release forms carry `bN`/`rcN`, stable is bare `X.Y.Z`). But the operator works from an
   **editable install** in the devcontainer, so the moment that string is a bare `X.Y.Z` —
   between betas, or at a stable cut — the bench silently loses `dev reg`, which is load-bearing
   project tooling (`dev reg 0 0 0x86 -f` is the held-erase-rail DMM proxy). Decide the override
   mechanism *before* implementation: an explicit env var (`FIRESTARTER_DEV_TOOLS=1`), detection
   of an editable/VCS install, or a separate `[dev]` pip extra. Whichever is chosen must fail
   **closed** for a wheel installed from PyPI and **open** for a source checkout — and must not
   be settable from a config file (same SAFE-01 reasoning that made `--destructive` CLI-only).
2. **Does a rejected dev command ID actually desync the COBS/CRC stream?** gh#8 asks for this
   proof, and the channel split makes it **load-bearing** rather than incidental: because the app
   and firmware channels install independently (`pip install --pre` vs `firestarter fw --pre`),
   **beta-app + stable-firmware becomes a likely pairing**, and in it the app offers `reg`/`addr`
   that the firmware will reject. Empirical: build a `DEV_TOOLS`-off firmware, send `cmd: 7` and
   `cmd: 8`, and confirm the next legitimate command still round-trips — i.e. the rejection path
   consumes its frame and does not leave the decoder mid-frame. Relevant precedent: the v1.12
   fail-closed `0xBB` path + host `ProtocolNotImplementedError` (`project_v112_milestone_closed`)
   may already be the correct rejection shape to reuse rather than inventing a second one.
3. **Is welding "beta channel" → "dev tools enabled" acceptable, or is a third tier needed?**
   The design makes every future beta a dev-tools build, so community beta testers — the exact
   audience v1.21 built `dev test` for and documented in `beta-testing-install.md` — receive the
   full hazardous surface (`reg`, `addr`, `write-cycle`, `fault-inject`) whether they want it or
   not. The gate then protects stable users and no one else. Options to weigh: accept it (opting
   into `--pre` is a deliberate act); or split "pre-release" from "dev-tools-enabled" into two
   axes, which reintroduces the second-artifact cost the channel split was chosen to avoid; or
   keep the beta CLI surface narrow and put only the *firmware* dev tools behind `--pre`. Needs
   an operator decision at scoping, not an implementer's guess.

## SDP surface retirement + behavioral proof (999.25) — added 2026-07-31

> Design: [`.planning/notes/sdp-surface-retirement-and-behavioral-proof.md`](../notes/sdp-surface-retirement-and-behavioral-proof.md).
> Stub: Phase 999.25 in `ROADMAP.md`.

1. **Can the inhibited-write leg be proven at all without AT28C silicon on the bench?** The leg's
   whole value is an inverted assertion — after `sdp_lock`, a write carrying `FLAG_SKIP_SDP_UNLOCK`
   must leave the chip **unchanged**. Nothing in operator inventory can exercise that end to end
   (`0x0D` is `UNVERIFIED`; no AT28C part — `project_phase83_shipped`). Decide before scoping what
   evidence the phase can actually produce: the Phase 116 trace harness can prove the *emission*
   (correct sequence, correct pinout remap, `/WE` asserted) and the native envs can prove the
   *plan derivation* and the read-back comparison logic, but the causal claim "the lock inhibited
   the write" is reachable **only** on real silicon, i.e. only from a community `dev test` report.
   State that split explicitly, or the phase will close claiming a proof it does not hold — the
   same overclaim class as v1.22's C-5 correction. Related: does the trace harness need a new
   fixture for a *locked* part, and is that even representable in a host-side stub, given the stub
   models the bus and not the die's protection state?
2. **Does `--sdp-relock` gate on verify success?** The v1.22 research recorded the relock as
   "opt-in only, gated on verify success" (`v1.22-research/SUMMARY.md:157`), and the reasoning is
   sound — relocking a part whose write did not verify protects a bad image behind a lock that
   cannot be read back and can only be cleared by another write. But the gate was never
   implemented or re-decided, and the deferral label ("v1.23+") now points at the wrong milestone.
   Confirm the polarity at scoping: does `--sdp-relock` silently skip the relock on verify
   failure (and say so loudly), refuse the whole operation up front, or relock regardless? The
   first is the only one consistent with "the attractor should be the state the user can recover
   from" (the rationale behind auto-unlock policy (d), `PROJECT.md:671`).

## Is there an independent second source for the PROGRAMMING axis? — added 2026-08-20

> Context: the pinout axis just acquired one. See
> [`.planning/todos/pending/onerom-pinout-external-corroboration-gate.md`](../todos/pending/onerom-pinout-external-corroboration-gate.md).

1. **Does a machine-readable, independently-derived source exist for `vpp_mv`,
   `pulse_duration_us`, `algorithm` and page size — the way One ROM's `chip-types.json` now
   does for bus maps?** The One ROM cross-check (2026-08-20) corroborated 12 of our 15
   `pinouts.json` families against an oracle with no `infoic.xml` lineage, validated by an
   emulator working in-circuit. But One ROM never programs a chip, so it is silent on every
   field where our actual defects have landed: the 4.5 V premise disproved in Phase 148 (5
   files, not 2), the 128/64 B page seam in Phase 149, the deleted `CTRL_VPE_ENABLE` assert
   behind the Phase 145 W27C512 byte-0 failure, `pulse_duration_us`, and the suspected VPP
   droop still standing as the Phase 99 AM27C020 explanation. That axis has exactly **one**
   source — `infoic.xml` — plus bench silicon for the handful of parts in operator inventory.
   A decode bug there is currently unfalsifiable except by bench or datasheet re-read.
   Candidates worth assessing: minipro/TL866 device tables, Wellon programmer tables, GQ-4x,
   EzoFlash, other open programmer firmware. **Hard filter: most of these are infoic forks
   or share its ancestry — a fork is not an independent oracle and would manufacture false
   confidence.** Establish lineage before treating any candidate as corroborating, and record
   the lineage finding even for the ones that fail the filter, so this does not get re-asked.
2. **If no independent source exists, what is the cheapest substitute?** Options include a
   datasheet-extraction pass over `firestarter_app/datasheets/` scored against the generated
   DB (the `devtest-rootcause` skill already reads datasheets for exactly this purpose, one
   chip at a time — the question is whether it generalises to a sweep), or accepting that the
   programming axis stays bench-only and instead investing in making community `dev test`
   reports the corroboration channel. The second is already partly built and would make the
   answer to (1) matter less — worth deciding which before scoping either.
3. **Should `pinouts.json` itself be reclassified?** It is hand-maintained and read as an
   *input* by `tools/build_db.py:23`, so the "generated, never hand-edit" protection around
   `chip_database.json` does not cover it, and nothing else does either — 255 chips ride
   `DIP32_SST39SF040` alone. The corroboration test in the linked todo closes most of that
   gap, but it leaves `DIP24_2532` (no external counterpart) and any newly-added family
   unguarded. Is a datasheet-citation requirement per family (a `comment` field with a
   sourced claim, as `DIP32_27C020` already carries) worth making mandatory?

## Host `tools/` checker apparatus — retire or keep? — added 2026-09-12

Source: `/gsd-explore` session 2026-09-12 (operator reading through `firestarter_app/tools/`,
suspecting over-engineering). See `notes/host-tools-checker-apparatus-audit.md` and
`seeds/phase-gate-expiry-discipline.md`. Measured: ten `check_*.py` gates, 3,984 lines plus
3,537 lines of their own tests, guarding a 21,153-line product. All ten report zero findings on
every run. Each locks in one decision from one phase; none has ever been retired.

1. **Is each gate actually reachable from CI?** Only `check_mypy_watermark.py` is named in
   `ci.yml`. The other nine reach CI solely through `pytest tests/`, and only where their test
   file invokes them against the **real tree** rather than a fixture. A static grep cannot
   settle this — a test file mentioning a checker is not the same as a clean-tree control test.
   Must be read per gate; a gate reachable from nothing is already dead.

2. **Is the invariant already covered by a unit test on the guarded module?** If
   `sdp_capability.py`'s own tests already assert the allow-set is not widenable, the 612-line
   AST gate guarding a 246-line file is redundant. Answer per gate, against the guarded
   module's test file — not in aggregate.

3. **Is the risk still live?** A gate preventing a mistake the code's current shape makes
   impossible is archaeology, not defence. Note that "it passes" is not a reason to keep one —
   all ten pass, which is the finding rather than a defence.

4. **For each survivor, what is its retirement condition?** Record it in the gate itself, per
   the `phase-gate-expiry-discipline` seed, so the next reader is not re-deriving this audit.

Non-goal: re-litigating gate quality. These are well built — each reports its scan surface
(none is a silent zero-scan), each carries planted-violation fixtures, and
`check_mypy_watermark` deliberately fails closed on mypy's rc=2. The question is whether they
still earn their mass.

## Which host tools are doing GSD's work? — added 2026-09-12

Source: same session, raised by the operator. See `notes/host-tools-checker-apparatus-audit.md`
§"tools doing GSD's work, inside the product repo". Several `firestarter_app/tools/` scripts
exist to produce evidence for GSD phase records rather than to serve the product — their
docstrings cite phases, plan numbers and `D-NN` decisions directly (`measure_plan_shapes.py`:
*"the frozen half of D-10's no-drop proof (Phase 175, plan 175-03)"*).

1. **Who is each candidate's real consumer?** For `audit_coverage_matrix.py`, `diff_db.py`,
   `measure_plan_shapes.py`, `measure_part_number_delta.py`, `snapshot_report_shapes.py`,
   `build_devtest_issue_corpus.py`: a phase record or GSD gate → process; the CLI, the database
   build, or a user-facing command → product. Some are genuinely mixed (`diff_db.py` plausibly
   serves DB regeneration *and* phase evidence), and the mixed ones are the interesting cases.

2. **Does it write outside its own repo?** `audit_coverage_matrix.py` resolves `_REPO_ROOT`
   three `dirname()` hops up — to the **meta** repo — and writes
   `.planning/v1.3-COVERAGE-MATRIX.md` plus a mutated `.planning/v1.3-defect-coverage-ids.json`
   there. In a standalone clone of `henols/firestarter_app` the same arithmetic writes a
   `.planning/` tree into the parent of the clone, outside the repository. That is a defect to
   fix whatever the answer to (1) — audit the other candidates for the same shape.

3. **Where does each belong instead?** Candidates: the meta repo's `tools/` (today only
   `catalog/`), a GSD skill owning its own copy, or deletion once the phase it served is closed
   and its artifact frozen. Constraint: a skill must own its scripts rather than importing from
   `firestarter_app/tools/`, so relocation must not create a cross-repo import. Tools importing
   `firestarter.*` need the package installed — a meta-repo home must account for that.

4. **Second-order — the citations.** These docstrings violate `CLAUDE.md`'s non-overridable
   no-comments rule for anything under `firestarter_app/`. Stripping them is not the fix on its
   own: a tool whose only rationale is "the frozen half of D-10's no-drop proof" cannot be
   given a product-facing docstring, and that inability is itself the placement signal. Resolve
   placement first.
