# Phase 145: Bench Validation - Context

**Gathered:** 2026-08-15
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase puts the v1.31 per-byte program loop on **real silicon** for the one protocol the
operator's inventory can carry, and records the other two honestly rather than inferring them.

What it delivers:

1. A full 64 KiB write→read→verify on **W27C512** (`0x07`) on **Leonardo + Rev 2.0**, three
   cycles deep, with per-run evidence (`BENCH-01`).
2. Two **skipped-with-reason disposition records** — `0x08` (AM27C020) and `0x0B` (M2716/M2732)
   — each naming the missing part and its last known bench state, neither inferred from the
   `0x07` result (`BENCH-02`).
3. A machine-checked proof that **no chip's `support_status` changed** anywhere in v1.31
   (`BENCH-03`).
4. The discharge of one inherited hand-off: **real intra-block progress-bar motion** on
   hardware (143 H4 / 144 H6), which no off-hardware proof could reach.

**Not in this phase:** any source change to firmware or host — this phase measures a built image,
it does not modify one (D-16); the honesty ledger, claim gate, gh#15 reconciliation and all
documentation (Phase 146); any change to a chip's `support_status`; any comparative claim that
v1.31 programs *better* than what preceded it (D-08); any claim of datasheet conformance — the
6.25 V program-VCC ceiling is unreachable on this shield and that debt is the milestone's, not
this phase's to discharge.

</domain>

<decisions>
## Implementation Decisions

### Bench inventory and identity

- **D-01:** **`BENCH-01` runs on the Winbond W27C512, on Leonardo, with the Rev 2.0 shield.** Measured from the shipped DB: `algorithm 7`, `pulse_duration 100 us`, `vpp 12V`, `EEPROM`, 65536 B, chip-id `0xda08`. It is the only `0x07` part on this bench that is **electrically erasable**, which is precisely what makes a repeatable multi-cycle full-chip proof affordable — the ST/TI UV parts are one-shot with no eraser on hand. The **TMS27C512 is deliberately not spent**; a true-UV `0x07` data point is not worth an irreversible part when the algorithm under test is identical. Rev 2.0 is chosen over Rev 2.2 because Phase 99 (`0x08`) and Phase 79 (the 25 V VPE rail) both ran on it, so any figure this phase produces is directly comparable to the existing record. Board identity is confirmed by **silkscreen, by eye, by the operator** — the EEPROM `hw_revision` byte cannot distinguish 2.0 from 2.2 from the modified Rev 0.

- **D-02:** **Both opportunistic protocols are skipped, and each skip is a full disposition record — not a line.** Neither an AM27C020 nor an M2716/M2732 is on the bench (operator, this session). Each record names: the missing part; the last known bench state with its numbers (`0x08` — Phase 99's write#1 60/64 then write#2 0/64 at stable idle VPP, carried as **FUT-08**, leading hypothesis program-window VPP-under-load droop, never instrumented; `0x0B` — Phase 79's rail-corrected 22.4 V DMM / 23.9 V firmware VPE reading at max pot, graduation parked "when a part is on hand", chips best-effort `supported` under operator override D-07); and an explicit **"NOT inferred from the `0x07` result"** sentence. `BENCH-02`'s own wording demands the naming, and Phase 146's ledger will cite these records rather than re-deriving them.

- **D-03:** **If plain `write` does not erase the W27C512 on the `0x07` path, `BENCH-01` falls back to a pure 1→0 program proof — never to `-b`.** The record is genuinely unresolved here: firmware erase is gated on `FLAG_CAN_ERASE`, which W27C512 now carries via electrical-type `EEPROM`, but the note says "firmware-supported, operator-bench-pending", and the older recorded behaviour was `ERROR: Not supported`. **Establishing which is true is pre-flight work, not a discovery mid-write.** The fallback is Phase 99's shape: verify a region reads all-`0xFF`, write a distinctive pattern into it, read back byte-exact — every target bit is a legal bit-clear, so the program path is isolated with no erase dependency. **`write -b` is forbidden as the workaround**: it sets `FLAG_SKIP_ERASE` and can report "successful" while producing bad bytes, which is the exact false-green this milestone exists to not commit.

### The `0x07` evidence bar

- **D-04:** **Coverage is the full 64 KiB, not a region.** All 65536 bytes: 64 blocks of 1024 B, the per-block VPE hold, and a genuinely long write. `BENCH-01`'s own text says "a full write→read→verify" and any smaller run is a narrowing. It also makes the run do double duty — see D-11.

- **D-05:** **Three write cycles, and a DIFFERENT image on each.** The erasability D-01 bought is what makes N≥3 affordable, and a different image per cycle is what makes cycles 2 and 3 mean anything: rewriting the same bytes over an unerased chip needs no bit to flip at all and would pass trivially. Three distinct images force real erase-then-program transitions every cycle.

- **D-06:** **Both oracles are recorded, separately, on their own lines.** The CLI's own verify verdict **and** an independent SHA-256 compare of source against a fresh read-back file (the Phase 99 `SHA256SUMS.txt` pattern). They are not merged into one verdict: the thing under test and the thing judging it must not be the same code path, and a **disagreement between them must be visible** rather than averaged away.

- **D-07:** **Read stability is measured per write cycle, not once at the end.** Each of the three cycles is followed by repeated read-backs compared to each other and to source. Program repeatability and read repeatability are different failure modes; `0x08`'s history is precisely a part that reads stably and programs unreliably.

- **D-08:** **No pre-v1.31 control run.** The milestone claims **fidelity, not improvement**, and no `BENCH-*` requirement asks for a differential. A control would cost a reflash cycle plus chip wear and would invite a comparative claim the 6.25 V evidence ceiling does not support.

- **D-09:** **The pass rule is 3/3 byte-exact on both oracles — with exactly one clean re-seat allowed.** A single failure **attributable to a named physical cause** (re-seat, chip-id mismatch, VPP out of band) may be discarded and that cycle re-run once. **Both the discarded failure and the re-run are recorded** — the allowance is a documented re-run, never a quiet retry. Anything else is a fail and triggers D-13.

### Inherited hand-offs from Phases 143 and 144

- **D-10:** **Real bar motion is discharged two ways — machine-counted frames AND operator eyes-on.** The machine half is primary: capture raw stderr with timestamps and count distinct progress updates **per 1024-byte block**; more than one update inside a single block **is** intra-block motion, which is a checkable claim rather than an impression. The operator half confirms what the terminal actually looked like — a smoothly moving bar, not a burst of frames arriving at the end. Note the constraint that makes this reachable at all: the emission is **`leonardo`-only** (compiled out on `SERIAL_ON_IO` targets), and this phase runs on Leonardo.

- **D-11:** **Timeout survival is claimed as free evidence from `BENCH-01`'s own completion.** The 64 KiB write either completes or the host times out; a completed run **is** the CAP-03 advertised-budget path holding on real hardware. It costs no extra bench time, so the record states it as a discharged hand-off rather than leaving Phase 146 to carry 143's H4 as unproven.

- **D-12:** **`--pulse-us` on silicon and the A1 per-pulse-overhead measurement are stretch items, attempted only if the required runs go clean.** Both are inherited (143 H4). If attempted, they are recorded as measured; **if not attempted, they are recorded as explicitly-not-discharged open hand-offs with no v1.31 owner** — Phase 146 is docs-and-claims only and cannot run a bench. Neither may be silently dropped. Of the two, `--pulse-us` above the **4687 µs** residual-gap threshold is the more informative: it would exercise the budget mechanism specifically rather than a write that merely fits inside the old 120 s fallback.

### Failure adjudication and disposition

- **D-13:** **A `0x07` failure stops the phase and hands to `/gsd-debug`.** After D-09's one allowed re-seat, the first genuine failure halts. Root-causing happens in a dedicated debug session with its own state — **this phase does not absorb a fix**. That keeps a validation phase from silently becoming an implementation phase, and it is why D-16's no-source-change invariant holds.

- **D-14:** **Two states only — validated, or skipped-with-reason. No third "inconclusive" state exists.** Anything that is not a clean pass is a fail; anything not attempted is a skip. The partial-result shape Phase 99 produced (60/64, then 0/64) would be a **fail** under this taxonomy, not a qualified pass. Decided **before** any run precisely so a partial result cannot be argued into the friendlier bucket afterwards.

- **D-15:** **`BENCH-03` is proven by a machine-checked diff across the WHOLE milestone range, not this phase's commits.** The requirement says "in this milestone". Measured at discussion time: `firestarter_app`'s v1.31 branch base is **`4d18b645`** (2026-08-07) and `git diff 4d18b645..HEAD -- firestarter/data/chip_database.json` is **empty** — so `BENCH-03` is already provably true today and the phase's job is to re-measure it at the tip and record the verbatim result. `chip_database.json` is **generated** (`tools/build_db.py`); the sole sanctioned `support_status` write locus is `build_db.py`, already machine-locked by `tools/check_no_community_support_status_write.py`.

### Cross-cutting bench mechanics

- **D-16:** **This phase changes no firmware and no host source.** It measures a built image. A plan that finds itself needing a source edit must stop and report (D-13's route), not absorb it. Consequence worth naming: the Leonardo flash tripwire handed forward as 144 H7 — **1766 B of headroom, armed at a 0 B growth band** — cannot be tripped by a phase that compiles nothing new, and the flashed image's size is recorded to show it.

- **D-17:** **No `--force`, anywhere. A guard-blocked run is a bench fault to fix in pre-flight, not to bypass.** The W27C512's known `VPP is high: 13.1V > 12.0V` init guard has historically been force-bypassed on this board, and the operator has previously said "use force and ignore vpp" — **that standing permission is withdrawn for this phase**. If the guard fires, the pot is adjusted until VPP reads in band and the run restarts clean. Phase 99's Gate 1 recorded `--force used? No` as a load-bearing line and this phase does the same. **The operator adjusts the pot himself** — state the target, wait, take **one** confirming read; never a live monitor loop.

- **D-18:** **Re-flash is mandatory and the image is identified by COMMIT, never by version string.** 144 H6 / 143 H4: a stale pre-CAP-02 v1.31 image **cannot even connect** (BF-1), so "whatever is on the board" is not a safe assumption. Record the firmware commit under test, the `avrdude` verified byte count, and the reported version string separately — the host **cannot see a firmware prerelease suffix**, so the version string alone never identifies a build. Leonardo is **chip-out-sideload EXEMPT** (that rule is Uno-class only), so the reflash may happen with the part seated.

- **D-19:** **Claude drives the serial and CLI side; the operator owns the physical.** USB passthrough reaches `/dev/ttyACM*` from the devcontainer, so Claude runs `fw`, `hw`, `read`, `write`, `vpp` and captures logs directly. **Operator-only:** seating and removing the chip, reading the silkscreen, adjusting the pot, taking any DMM reading, and the D-10 eyes-on confirmation. **No port is visible at discussion time** — nothing is attached yet, and `/dev/ttyACM*` numbering shuffles across replug, so `controller:` identity is verified per task, not assumed.

- **D-20:** **This phase must not run under `--auto` or `--chain`.** Auto-modes **auto-approve** `human-verify` gates; `autonomous: false` is not self-protecting. Every operator gate in this phase is real.

### Claude's Discretion

An index of discretionary items, not a second definition site. The IDs are deliberately unbolded
here: a `- **D-NN**` bullet without a `:` or ` — ` inside the bold makes the decision-coverage gate
fail closed with `reason: could-not-parse`.

- The **write-image pattern** (D-05's three images). The operator said "you decide"; the binding
  constraint is that a mismatch must be **attributable to an address**, not merely counted — the
  distinction that root-caused Phase 97's pin-31 defect. An address-derived pattern satisfies this;
  `tools/gen_test_image.py` exists and may be used if it does.
- The **pre-flight gate structure and the bench-log shape**. `99-03-BENCH-LOG.md`'s gated form
  (identity table → authorized spend → verdict per gate, with "not measured" recorded honestly
  where a reading is tooling-blocked) is the house precedent; the record's filename and section
  order are Claude's.
- The **frame-counting method** for D-10 — how stderr is captured and how per-block updates are
  counted — provided the resulting claim is checkable rather than narrative.
- **Plan decomposition and wave structure**, including where the pre-flight erase-capability
  determination (D-03) sits relative to the first spend.
- The exact **command forms** for read-back capture. Note `dev read` prints a non-binary stream and
  does **not** honour `-o`; a clean 65536-byte read-back needs `read <chip> <file>`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase requirements and milestone framing
- `.planning/REQUIREMENTS.md` §"Bench Validation" — BENCH-01…03, exact text (lines 245–252).
- `.planning/ROADMAP.md` §"Phase 145: Bench Validation" — goal, dependency on Phase 144, and the
  four success criteria (lines 485–497).
- `.planning/PROJECT.md` §"Current Milestone: v1.31" — the **6.25 V program-VCC evidence ceiling**
  and the asymmetric-bench-coverage framing this phase's records must not overstate.
- `.planning/STATE.md` lines 119–124 — the standing bench restrictions for this phase (operator-only
  physical work; no `--auto`/`--chain`).

### The hand-offs this phase consumes
- `.planning/phases/144-tests-build-verification/144-TEST-RECORD.md` — **§10 H6** (all bench evidence,
  and the must-re-flash instruction), **§10 H7** (the 1766 B Leonardo headroom at a 0 B tripwire),
  **§6 item 4** (the standing no-bench-claim boundary this phase now moves), **§2.1** the flash/RAM
  figures the flashed image should match.
- `.planning/phases/143-host-timeout-progress-pulse-override/143-HOST-RECORD.md` — **§1** the honest
  headline and the explicit statement that bar motion, long-write survival and A1 are Phase 145's;
  **§4** the padding rule `padded_s = ceil(raw_pulse_only_us / 1e6) * 2 + 2` and the `[ASSUMED]`
  ~20-60 µs/pulse A1 figure D-12 may measure; **§5 items 1, 5, 6, 7** the `leonardo`-only emission,
  the **4687 µs** residual-gap threshold, and `--pulse-us`'s bound provenance; **§10 H4**.
- `.planning/phases/142-high-voltage-routing/142-VPP-RECORD.md` — the VPP/VPE routing this phase
  exercises for real.

### Bench precedent — the house shape for this phase's own record
- `.planning/phases/99-bench-ledger-graduation-gate-evidence-ledger-update/99-03-BENCH-LOG.md` —
  **Gate 1** (the identity table: controller, port, silkscreen, seated chip, R1/R2, firmware commit
  under test, reflash proof, VPP confirmation, `--force used? No`); **Gate 2** (authorized spend,
  the honest methodology-deviation section, SHA compare, N-stability). This is the form D-19 follows.
  It is also the `0x08` prior state D-02's skip record must cite.
- `.planning/phases/79-*/` and the Phase 79 record — the `0x0B` 25 V NMOS prior state D-02 cites:
  VPE 22.4 V DMM / 23.9 V firmware at max pot, graduation parked awaiting a part.

### Host and firmware artifacts this phase drives
- `firestarter_app/firestarter/data/chip_database.json` — the D-15 diff target. **Generated** by
  `firestarter_app/tools/build_db.py`; never hand-edited.
- `firestarter_app/tools/check_no_community_support_status_write.py` — the existing machine lock on
  `support_status` writes; D-15's proof composes with it rather than duplicating it.
- `firestarter_app/firestarter/cli_handlers.py` — `write` and its `--pulse-us` flag (:576–:692), the
  `dev` command group, and the gated `dev` subcommands.
- `firestarter_app/firestarter/eprom_operations.py` — the `pulse_us` transport (:1869–:1894), the
  `0x0B` over-cap refusal message (:259–:287), and the D-10 fallback comment (:109–:125).
- `firestarter_app/tools/gen_test_image.py` — a candidate image generator for D-05.
- `firestarter/scripts/baseline/size_baseline.json` — the re-anchored v1.31 figures
  (24824 / 24874 / 26906) the flashed Leonardo image should match (D-16, 144 H7).

### Operator-context constraints that are easy to violate
- `firestarter_app/CLAUDE.md` and `firestarter/CLAUDE.md` — command surface and the W27C512 /
  `0x07` dispatch notes.
- The `write -b` footgun (`FLAG_SKIP_ERASE`), the ST-M27C512-vs-Winbond-W27C512 chip-id distinction
  (`0x203d` UV/13 V vs `0xda08` EEPROM/12 V), and the fact that `vpp`/`vpe` are **continuous
  monitors** that only flush on exit (sample with `timeout -s INT N firestarter vpp`).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`99-03-BENCH-LOG.md`'s gate structure** — a working template for a bench record that survives
  audit: an identity table, an explicit operator authorization line per spend, honest
  "not measured" entries with reasons, and SHAs kept in a separate `SHA256SUMS.txt` rather than
  inline in the narrative.
- **`tools/gen_test_image.py`** — an existing image generator, if it satisfies D-05's
  address-attributable constraint.
- **`tools/check_no_community_support_status_write.py`** — `support_status` writes are already
  machine-locked to `build_db.py`. D-15 measures the outcome; this gate protects the mechanism.
- **`firestarter read <chip> <file>`** — the clean binary read-back path. `dev read` is not it
  (non-binary stream, ignores `-o`).
- **`dev consistency-check --runs N --output-dir`** — the existing read-stability harness D-07 needs;
  it writes `run_NN.bin` files that can be SHA-compared directly.

### Established Patterns
- **The chip-id check fails safe.** A plain `write` aborts on a chip-id mismatch with no `--force`,
  which is how the v1.18 P97 wrong-part mix-up was caught before any silicon was spent. Seating the
  ST M27C512 instead of the Winbond W27C512 would abort rather than damage.
- **`dev write-cycle` erases first**, so it has historically been unusable on parts whose standalone
  erase is unsupported. Whether it is now usable on W27C512 depends on the same unresolved
  `FLAG_CAN_ERASE` question as D-03 — determine it, don't assume it.
- **Commit before running either repo's suite.** `firestarter/tests/test_flash_path_record_sync.py`
  asserts the **whole** firmware repo's `git status --porcelain`, and the host's
  `test_py32_flash_map_host.py` asserts the same for the *sibling* firmware repo — an untracked
  bench artifact in the wrong directory turns a green suite RED.
- **Evidence is recorded verbatim, including failures.** Every prior bench phase in this project
  that recorded a partial or blocked result (Phase 79's NOT-CLEARED, Phase 99's DEFER, Phase 97's
  "not measured") is cited today as usable evidence; a rounded-off pass would not have been.

### Integration Points
- `/dev/ttyACM*` via devcontainer USB passthrough — Claude's half of D-19.
- `.planning/phases/145-bench-validation/` — the bench record, the raw logs, and the SHA manifest.
- No source integration: D-16 means this phase writes no code into either sub-repo.

</code_context>

<specifics>
## Specific Ideas

- **The chip is the Winbond `0xda08`, not the ST `0x203d`.** Both are called "512" and both are
  28-pin `0x07`; they differ in erasability and in VPP (12 V vs 13 V). Confirm by chip-id before
  the first spend.
- **"More than one progress update inside a single 1024-byte block" is the bar-motion claim.**
  State it in those terms (D-10) — it is checkable; "the bar moved smoothly" is not.
- **`--force used? No` is a load-bearing line in the record**, not a formality (D-17).
- **The `0x08` skip record must carry `60/64` and `0/64`, and the `0x0B` record `22.4 V`.** A skip
  that names only the missing part loses the evidence Phase 146 will want to cite.
- **`BENCH-03` is already provably true** — `chip_database.json` has zero diff from the app's v1.31
  base `4d18b645`. The phase re-measures at the tip; it should not discover this for the first time.

</specifics>

<deferred>
## Deferred Ideas

- **A true-UV `0x07` data point on the TMS27C512** — deliberately not spent (D-01). Reachable only
  by consuming an irreversible part; revisit if a UV eraser ever joins the bench.
- **`0x08` (AM27C020) and `0x0B` (M2716/M2732) bench validation** — blocked on parts, not on code
  (D-02). `0x08` additionally carries **FUT-08**: program-window VPP-under-load droop, hypothesised
  and never instrumented, and the held-rail DMM proxy that would measure it is itself blocked by
  DTR-reset-on-close.
- **`--pulse-us` exercised on real silicon** and **the A1 per-pulse-overhead measurement** — stretch
  items under D-12; if not reached, they carry forward with **no v1.31 owner**.
- **The `--pulse-us` above-4687 µs budget-mechanism proof** — the sharpest available test of the
  CAP-03 path, folded into the same stretch bucket.
- **A pre-v1.31 differential control run** — rejected by D-08, not deferred for lack of time; the
  milestone deliberately makes no comparative claim.

### Reviewed Todos (not folded)

The first `todo.match-phase 145` run returned keyword matches; **none folded** — every one is
other-protocol or firmware-behaviour work in a phase that changes no source (D-16). Named matches:
"CONFIG_VERSION is not bumped when a calibration default changes" (0.9, firmware), "FM1608 byte 0
write never lands" (0.9, a different write path), "AT28C256 write-path failure (gh#20)" (0.6, `0x0D`
EEPROM, not 27C), "avrdude MCU-detection fallback" (0.6), "frame-level deadline to the firmware COBS
decoder (WR-01)" (0.6), "Photograph operator's Modified Rev 0 board" (0.6). The matches are keyword
artifacts — "firmware", "status", "phase", "bench" — not scope overlap. **Tool note:** a re-run of
the same query after `.planning/phases/145-bench-validation/` was created returned `todo_count: 0`;
do not treat a zero result from that handler as evidence that no todos matched.

</deferred>

---

*Phase: 145-Bench Validation*
*Context gathered: 2026-08-15*
