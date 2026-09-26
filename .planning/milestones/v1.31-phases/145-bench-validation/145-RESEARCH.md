# Phase 145: Bench Validation — Research

**Researched:** 2026-08-15
**Domain:** Hardware bench validation of an already-built firmware image — measurement, evidence capture and honest disposition. **No source change** (D-16).
**Confidence:** HIGH on everything resolvable in code; MEDIUM on two timing predictions that only the bench can settle (both named, both with mitigations).

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** **`BENCH-01` runs on the Winbond W27C512, on Leonardo, with the Rev 2.0 shield.** Measured from the shipped DB: `algorithm 7`, `pulse_duration 100 us`, `vpp 12V`, `EEPROM`, 65536 B, chip-id `0xda08`. It is the only `0x07` part on this bench that is **electrically erasable**, which is precisely what makes a repeatable multi-cycle full-chip proof affordable — the ST/TI UV parts are one-shot with no eraser on hand. The **TMS27C512 is deliberately not spent**; a true-UV `0x07` data point is not worth an irreversible part when the algorithm under test is identical. Rev 2.0 is chosen over Rev 2.2 because Phase 99 (`0x08`) and Phase 79 (the 25 V VPE rail) both ran on it, so any figure this phase produces is directly comparable to the existing record. Board identity is confirmed by **silkscreen, by eye, by the operator** — the EEPROM `hw_revision` byte cannot distinguish 2.0 from 2.2 from the modified Rev 0.

- **D-02:** **Both opportunistic protocols are skipped, and each skip is a full disposition record — not a line.** Neither an AM27C020 nor an M2716/M2732 is on the bench (operator, this session). Each record names: the missing part; the last known bench state with its numbers (`0x08` — Phase 99's write#1 60/64 then write#2 0/64 at stable idle VPP, carried as **FUT-08**, leading hypothesis program-window VPP-under-load droop, never instrumented; `0x0B` — Phase 79's rail-corrected 22.4 V DMM / 23.9 V firmware VPE reading at max pot, graduation parked "when a part is on hand", chips best-effort `supported` under operator override D-07); and an explicit **"NOT inferred from the `0x07` result"** sentence. `BENCH-02`'s own wording demands the naming, and Phase 146's ledger will cite these records rather than re-deriving them.

- **D-03:** **If plain `write` does not erase the W27C512 on the `0x07` path, `BENCH-01` falls back to a pure 1→0 program proof — never to `-b`.** The record is genuinely unresolved here: firmware erase is gated on `FLAG_CAN_ERASE`, which W27C512 now carries via electrical-type `EEPROM`, but the note says "firmware-supported, operator-bench-pending", and the older recorded behaviour was `ERROR: Not supported`. **Establishing which is true is pre-flight work, not a discovery mid-write.** The fallback is Phase 99's shape: verify a region reads all-`0xFF`, write a distinctive pattern into it, read back byte-exact — every target bit is a legal bit-clear, so the program path is isolated with no erase dependency. **`write -b` is forbidden as the workaround**: it sets `FLAG_SKIP_ERASE` and can report "successful" while producing bad bytes, which is the exact false-green this milestone exists to not commit.

- **D-04:** **Coverage is the full 64 KiB, not a region.** All 65536 bytes: 64 blocks of 1024 B, the per-block VPE hold, and a genuinely long write. `BENCH-01`'s own text says "a full write→read→verify" and any smaller run is a narrowing. It also makes the run do double duty — see D-11.

- **D-05:** **Three write cycles, and a DIFFERENT image on each.** The erasability D-01 bought is what makes N≥3 affordable, and a different image per cycle is what makes cycles 2 and 3 mean anything: rewriting the same bytes over an unerased chip needs no bit to flip at all and would pass trivially. Three distinct images force real erase-then-program transitions every cycle.

- **D-06:** **Both oracles are recorded, separately, on their own lines.** The CLI's own verify verdict **and** an independent SHA-256 compare of source against a fresh read-back file (the Phase 99 `SHA256SUMS.txt` pattern). They are not merged into one verdict: the thing under test and the thing judging it must not be the same code path, and a **disagreement between them must be visible** rather than averaged away.

- **D-07:** **Read stability is measured per write cycle, not once at the end.** Each of the three cycles is followed by repeated read-backs compared to each other and to source. Program repeatability and read repeatability are different failure modes; `0x08`'s history is precisely a part that reads stably and programs unreliably.

- **D-08:** **No pre-v1.31 control run.** The milestone claims **fidelity, not improvement**, and no `BENCH-*` requirement asks for a differential. A control would cost a reflash cycle plus chip wear and would invite a comparative claim the 6.25 V evidence ceiling does not support.

- **D-09:** **The pass rule is 3/3 byte-exact on both oracles — with exactly one clean re-seat allowed.** A single failure **attributable to a named physical cause** (re-seat, chip-id mismatch, VPP out of band) may be discarded and that cycle re-run once. **Both the discarded failure and the re-run are recorded** — the allowance is a documented re-run, never a quiet retry. Anything else is a fail and triggers D-13.

- **D-10:** **Real bar motion is discharged two ways — machine-counted frames AND operator eyes-on.** The machine half is primary: capture raw stderr with timestamps and count distinct progress updates **per 1024-byte block**; more than one update inside a single block **is** intra-block motion, which is a checkable claim rather than an impression. The operator half confirms what the terminal actually looked like — a smoothly moving bar, not a burst of frames arriving at the end. Note the constraint that makes this reachable at all: the emission is **`leonardo`-only** (compiled out on `SERIAL_ON_IO` targets), and this phase runs on Leonardo.

- **D-11:** **Timeout survival is claimed as free evidence from `BENCH-01`'s own completion.** The 64 KiB write either completes or the host times out; a completed run **is** the CAP-03 advertised-budget path holding on real hardware. It costs no extra bench time, so the record states it as a discharged hand-off rather than leaving Phase 146 to carry 143's H4 as unproven.

- **D-12:** **`--pulse-us` on silicon and the A1 per-pulse-overhead measurement are stretch items, attempted only if the required runs go clean.** Both are inherited (143 H4). If attempted, they are recorded as measured; **if not attempted, they are recorded as explicitly-not-discharged open hand-offs with no v1.31 owner** — Phase 146 is docs-and-claims only and cannot run a bench. Neither may be silently dropped. Of the two, `--pulse-us` above the **4687 µs** residual-gap threshold is the more informative: it would exercise the budget mechanism specifically rather than a write that merely fits inside the old 120 s fallback.

- **D-13:** **A `0x07` failure stops the phase and hands to `/gsd-debug`.** After D-09's one allowed re-seat, the first genuine failure halts. Root-causing happens in a dedicated debug session with its own state — **this phase does not absorb a fix**. That keeps a validation phase from silently becoming an implementation phase, and it is why D-16's no-source-change invariant holds.

- **D-14:** **Two states only — validated, or skipped-with-reason. No third "inconclusive" state exists.** Anything that is not a clean pass is a fail; anything not attempted is a skip. The partial-result shape Phase 99 produced (60/64, then 0/64) would be a **fail** under this taxonomy, not a qualified pass. Decided **before** any run precisely so a partial result cannot be argued into the friendlier bucket afterwards.

- **D-15:** **`BENCH-03` is proven by a machine-checked diff across the WHOLE milestone range, not this phase's commits.** The requirement says "in this milestone". Measured at discussion time: `firestarter_app`'s v1.31 branch base is **`4d18b645`** (2026-08-07) and `git diff 4d18b645..HEAD -- firestarter/data/chip_database.json` is **empty** — so `BENCH-03` is already provably true today and the phase's job is to re-measure it at the tip and record the verbatim result. `chip_database.json` is **generated** (`tools/build_db.py`); the sole sanctioned `support_status` write locus is `build_db.py`, already machine-locked by `tools/check_no_community_support_status_write.py`.

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

### Deferred Ideas (OUT OF SCOPE)

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
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description (verbatim, `.planning/REQUIREMENTS.md:246-252`) | Research Support |
|----|-------------|------------------|
| **BENCH-01** | `0x07` is bench-validated on W27C512 or TMS27C512 via a full write→read→verify on Leonardo, recorded with per-run evidence. | §RQ-1 (erase resolved: plain `write` DOES erase), §RQ-2 (verified address-attributable image recipe + the erase oracle it buys), §RQ-3 (exact `read`/`verify`/`consistency-check` forms), §RQ-7 (VPP band), §Code Examples |
| **BENCH-02** | `0x08` (AM27C020) and `0x0B` (M2716/M2732) are validated **if the parts are available**; otherwise each is recorded **skipped-with-reason naming the missing part** — never rubber-stamped, never inferred from the `0x07` result. | §RQ-8 (verbatim prior-state numbers with sources: 60/64, 0/64, 22.4 V / 23.9 V), §Record Template |
| **BENCH-03** | No chip's `support_status` changes in this milestone (D-07). | §RQ-6 — **already measured, empty diff, four independent legs + the histogram to quote** |
</phase_requirements>

---

## Summary

This phase runs zero new code. Everything it needs already exists and, on inspection, almost every
open question in the phase context is answerable **off the bench, from the source and the record**.
This research answers all nine, so the plan can be written as a sequence of commands with known
expected outputs rather than as a discovery exercise.

Three findings change the shape of the plan materially:

1. **D-03 is not open.** The W27C512 sends `flags=0x02` (`FLAG_CAN_ERASE`) on the wire today —
   computed by running the shipped host code — and the firmware's `eprom_write_init` calls
   `eprom_internal_erase()` whenever that bit is set and `FLAG_SKIP_ERASE` is not. The historical
   `ERROR: Not supported` is from **2026-05-21, before the v1.11 decode fix** (`cca7d62`), and the
   "operator-bench-pending" caveat is the v1.11 todo's own closing sentence, **superseded by
   Phase 77's bench proof** ("first hardware graduation ... write→auto-erase→program→verify
   bench-proven on a real non-blank W27C512 on the Leonardo") and Phase 91's PASS. Plain
   `firestarter write` erases. The fallback branch should be planned as an unused contingency, not
   as a coin-flip.

2. **D-10's literal claim is arithmetically unreachable at the database pulse, and the fix is one
   extra 25-second run.** The firmware's intra-block emission is **time-keyed at 1000 ms**
   (`EPROM_PROGRESS_EMIT_INTERVAL_MS`), and `last_emit_ms` is a **function-local re-initialised at
   the start of every block**. A 1024-byte block at the DB's 100 µs pulse takes roughly 350–700 ms
   (a recorded 64 KiB W27C512 Leonardo write is **22.84 s**), so **no block reaches the first
   emission** and the write bar is driven entirely by the host's chunk hand-off — every frame
   landing on an exact multiple of 1024. The evidence D-10 wants becomes reachable by adding a
   short `--pulse-us` run: at `--pulse-us 4688` a block takes ~5 s and yields ~5 frames, and a
   4096-byte (4-block) input costs ~25 s of bench time while simultaneously discharging D-12's
   `--pulse-us`-on-silicon item and the sharper above-4687 µs budget-mechanism proof.

3. **`firestarter fw --install` is the wrong reflash route (D-18).** It downloads a **GitHub release
   asset**; the v1.31 firmware branch has no release, so it would flash `beta` — a different image.
   The only route that flashes the tree under test is `pio run -t upload -e leonardo` from
   `/workspaces/firestarter`, exactly as Phase 99 did. Worse for identification: the v1.31 branch's
   `VERSION` is `"3.0.0b17"`, **byte-identical to its own fork point `3085084`**, while `origin/beta`
   is `"3.0.0b18"` — so a correctly flashed v1.31 image reports a version that looks *older* than
   beta. The commit plus the avrdude byte count (**26906 B**, matching `size_baseline.json`) are the
   only discriminators.

One hard operational tripwire was proven empirically this session: **a single untracked file
anywhere in `/workspaces/firestarter` turns 9 tests RED** — 5 in the firmware suite, 4 in the host
suite. Bench artifacts must land in the meta repo or `/tmp`, never in the firmware checkout.

**Primary recommendation:** structure the phase as Phase 99's gate ladder — Gate 0 off-bench
(BENCH-03 + image generation + BENCH-02 skip records, zero hardware), Gate 1 identity + reflash +
VPP, Gate 2 the three 64 KiB cycles, Gate 3 the short `--pulse-us` D-10/D-12 run — with the
`support_status` proof and both skip records fully written **before any silicon is touched**, so a
D-13 halt still lands BENCH-02 and BENCH-03 complete.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Erase-before-write decision | **Host DB layer** (`database.py::convert_to_programmer`) | Firmware `eprom_write_init` | The host derives `FLAG_CAN_ERASE` from `electrical.type`; the firmware only *obeys* the bit. Neither tier decides alone. |
| Program pulse width | **Host DB** (`pulse-delay` wire key) | Firmware `configure_eprom` fallback switch | DB supplies it; firmware falls back to 1000 µs (0x07) only when the host sends 0. `--pulse-us` overrides on the host side. |
| Per-byte program loop + verify | **Firmware** (`eprom.cpp::eprom_internal_write_execute_body`) | — | The thing under test. Host never sees individual pulses. |
| Write verdict (oracle 1) | **Firmware** (`VERIFY_PER_PULSE_PLUS_FINAL`) | Host renders `Write to … successful` | Firmware-side compare — same tier as the code under test. |
| Independent verdict (oracle 2) | **Host** (`read` → file → `sha256sum`) | Firmware CMD_READ streams bytes | Different firmware operation + host-side compare. This is what makes D-06's independence real. |
| Intra-block progress emission | **Firmware** (`#ifndef SERIAL_ON_IO`, 1000 ms cadence) | Host `_apply_write_progress` → tqdm | Leonardo-only, structurally. Host cannot manufacture it. |
| Per-response write timeout | **Firmware** (CAP-03 advertised budget) | Host uses it verbatim, no multiplier | D-09: only the firmware knows its own settle/verify costs. |
| VPP over/under band guard | **Firmware** (`eprom_check_vpp`) | Host only relays `vpp_mv` from DB | The guard compares an ADC read against `handle->vpp_mv ± band`. |
| Board/port identity | **Host** (`find_and_connect` / `fw`) | — | `-p` only *prefers* a port; it does not pin it. |
| Shield revision identity | **Operator eyes-on (silkscreen)** | EEPROM `hw_revision` byte | The byte cannot distinguish Rev 2.0 / 2.2 / modified Rev 0 (D-01). |

---

## Research Questions — Resolved

### RQ-1 (D-03) — Does plain `firestarter write` erase a W27C512 on the `0x07` path?

**YES. HIGH confidence. Resolved in code, corroborated by three prior bench records.**

**Host side.** `firestarter_app/firestarter/database.py:617-620` sets `FLAG_CAN_ERASE` when
`electrical-type ∈ {"EEPROM", "Flash/EEPROM"}` **and** `algorithm ∉ {5, 13}`. W27C512 is
`electrical.type = "EEPROM"`, `algorithm 7`. Executed against the shipped code this session
[VERIFIED: ran `EpromDatabase().convert_to_programmer()` on the live DB]:

| Chip | algo | wire `flags` | `FLAG_CAN_ERASE` | `vpp_mv` | `pulse-delay` | `chip-id` | `memory-size` |
|------|------|--------------|------------------|----------|---------------|-----------|---------------|
| **W27C512** | **7** | **0x02** | **True** | **12000** | **100** | **55816 (0xDA08)** | **65536** |
| M27C512 (ST) | 7 | 0x00 | False | 13000 | 100 | 8253 (0x203D) | 65536 |
| TMS27C512 (TI) | 7 | 0x00 | False | 13000 | 100 | 38789 (0x9785) | 65536 |
| AM27C020 | 8 | 0x00 | False | 13000 | 100 | 407 (0x197) | 262144 |
| M2716 | 11 | 0x00 | False | 25000 | 500 | 0 | 2048 |

Flag values: `FLAG_FORCE 0x01`, `FLAG_CAN_ERASE 0x02`, `FLAG_SKIP_ERASE 0x04`,
`FLAG_SKIP_BLANK_CHECK 0x08`.

**Firmware side.** `firestarter/src/proms/eprom.cpp:143-160` (`eprom_internal_write_init_body`):

```c
if (is_flag_set(FLAG_CAN_ERASE)) {
    if (!is_flag_set(FLAG_SKIP_ERASE)) {
        eprom_internal_erase(handle);
    } else {
        LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE);
    }
}
if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
    mem_util_blank_check(handle);
}
```

`eprom_internal_erase` (`eprom.cpp:588-604`) is real and implemented for this family: regulator on,
`delay(100)`, address `0x0000`, assert `CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE`, `delay(100)`, chip
enable, `mem_util_delay_us(pulse_delay)`, chip disable, HV all off.

The standalone `firestarter erase` path is gated at `eprom_operations.cpp:33-39`
(`if (!is_flag_set(FLAG_CAN_ERASE)) { LOG_ERROR_ID(MSG_ERR_NOT_SUPPORTED); return true; }`) —
**that line is the source of the historical `ERROR: Not supported`**, and it no longer fires for
W27C512 because the flag is now set.

**The record's apparent conflict, resolved chronologically** [CITED: `.planning/todos/completed/w27c512-eeprom-misclassification.md`, `.planning/MILESTONES.md:406`, `:356`, `:357`]:

| Date | Event | Effect |
|------|-------|--------|
| 2026-05-21 | Phase 24 bench: `firestarter erase W27C512` → `ERROR: Not supported` | `build_db.py` decoded W27C512 as UV-EPROM → flag never set |
| 2026-06-09 | v1.11 `cca7d62` fixes the infoic decode → `electrical.type = EEPROM` | Todo closes with *"**NOT yet bench-verified**: whether `firestarter erase W27C512` succeeds end-to-end is firmware-gated … needs an operator bench test"* ← **this is D-03's "operator-bench-pending"** |
| v1.14 Phase 77 | `convert_to_programmer` derives the flag from `electrical.type` | *"**First hardware graduation:** the full write→auto-erase→program→verify cycle is bench-proven on a real non-blank W27C512 on the Leonardo (clean no-`-b` write, independent read SHA-match…)"* |
| v1.16 Phase 91 | RCA: `write -b` was the test-method error | *"W27C512 (operator returned, chip-ID 0xDA08, **erase = `e16b2a5b`**) … graduated to PASS"* |
| v1.16 Phase 92 | `-b` decoupled from skip-erase | *"bench-confirmed on the seated W27C512"* |

**The cheapest single pre-flight command that settles it on the bench:**

```bash
firestarter erase W27C512 -b        # -b on `erase` ADDS a post-erase blank check (inverse polarity to `write -b`)
```
Exit 0 with the blank check passing proves (a) the op-layer `FLAG_CAN_ERASE` gate lets it through
and (b) the erase physically worked. `_build_op_flags(blank_check=True)` clears
`FLAG_SKIP_BLANK_CHECK`, which is what makes `configure_eprom` attach
`firestarter_operation_end = mem_util_blank_check` for `CMD_ERASE`. **Non-destructive on an
electrically-erasable part, and it also leaves the chip blank and ready for cycle 1.**

Zero-hardware corroboration, quotable straight into the record:
```
$ firestarter info W27C512
Type:               EEPROM
Can be erased:      yes (electrically erasable)
VPP:                12.0v
Chip ID:            0xda08
Pulse delay:        100µS
```

**Bonus — D-05's image sequence is itself a second, stronger erase oracle.** See RQ-2: with the
recommended images, **99.8 %** of bytes in cycle 1→2 require at least one `0→1` bit transition. If
the erase silently no-ops, those bytes cannot be programmed and cycle 2 fails with
`MSG_ERR_MAX_PULSES`. A clean cycle-2 PASS is positive proof the erase fired — no separate claim
needed.

---

### RQ-2 (D-05) — Is `tools/gen_test_image.py` address-attributable? Can it produce three distinct images?

**Distinct: yes. Address-attributable: NO — recommend a different generator.** HIGH confidence.

`firestarter_app/tools/gen_test_image.py` is 79 lines: `random.Random(seed)` → `size_bytes` of
pseudo-random data, prints SHA-256. CLI: `python tools/gen_test_image.py <size_bytes> <seed> <output_path>`.
Three distinct seeds give three distinct, reproducible 65536-byte images, and a byte diff always
tells you *which offset* mismatched (`cmp -l`).

**Why it does not satisfy the constraint as CONTEXT words it.** The binding requirement is that a
mismatch be *"attributable to an address … the distinction that root-caused Phase 97's pin-31
defect."* With pseudo-random data the mismatched **value** carries no address information — an
address-line aliasing fault (address N returning the byte belonging to address M) is *detected*
(~99.6 % of bytes mismatch) but not *diagnosed*: nothing in the data says "this byte came from M".
Phase 97's pin-31/A18 root-cause depended on exactly that decode step.

**Recommended replacement — verified this session.** A word-stamped address pattern: byte at offset
`N` carries the **low** byte of `N` when `N` is even and the **high** byte when `N` is odd, XOR a
per-image mask. Each aligned 2-byte word literally stamps its own 16-bit address.

```python
def img(size: int, mask: int) -> bytes:
    b = bytearray(size)
    for n in range(size):
        stamp = (n >> 8) & 0xFF if (n & 1) else n & 0xFF
        b[n] = stamp ^ mask
    return bytes(b)
# masks: image1=0x00, image2=0xFF, image3=0x5A
```

Measured properties over `size=65536` [VERIFIED: executed]:

| Property | image1 (0x00) | image2 (0xFF) | image3 (0x5A) |
|---|---|---|---|
| SHA-256 | `f72489604bfe917db7ee505e4d674576b2905a418e8dc55372b78dcab3e34e3a` | `b566c7a0319cc37051ec9c92bc1faef81f75e3740c7c6c8864778a549624fd96` | `74c359c8d8668fdc5778270d61cc3fbef55a1027999f20c5798a54bf0f6aea01` |
| bytes == `0xFF` | 128 (0.20 %) | 384 (0.59 %) | 128 (0.20 %) |
| distinct byte values | 256 | 256 | 256 |

- **Pairwise distinctness:** all three pairs differ in **65536/65536** bytes — D-05's "different image
  each cycle" is maximally satisfied.
- **Erase oracle:** bytes needing at least one `0→1` bit — cycle 1→2 **65408/65536 (99.8 %)**,
  cycle 2→3 **59392/65536 (90.6 %)**.
- **Address attributability (simulated A8-stuck-low):** 16384 mismatches, first at `0x0101`;
  observed byte `0x00` un-masks to `0x00`, offset is odd ⇒ high address byte ⇒ the byte belongs to
  an address whose high byte is `0x00`, i.e. `0x0001` — **naming A8 as the aliased line.**
- **Firmware-skip exposure:** only 0.2–0.6 % of bytes are `0xFF`, which `eprom.cpp:407`
  (`if (expected == 0xFF) continue;`) skips without a pulse. Those bytes are still covered by
  `VERIFY_PER_PULSE_PLUS_FINAL`'s final full-block read pass, so no coverage hole — but state the
  count in the record rather than implying 65536 bytes were pulsed.

**Where this lives (D-16).** This is 4 lines of throwaway generator, not a source change to either
sub-repo. Write it under the meta repo's phase directory (or `/tmp`) and record its SHA-256 output
alongside the images. It must **not** be added to `firestarter_app/tools/`.

**If the planner prefers zero new code**, `gen_test_image.py` is a legitimate fallback — but the
record must then carry an explicit non-claim: *"a mismatch's offset is identifiable; its value is
not decodable to a source address, so an address-line aliasing fault would be detected but not
localised."*

---

### RQ-3 (D-07 / D-06) — Exact CLI forms for clean read-back and read stability

**`firestarter read <chip> <file>`** — `cli_handlers.py:515-543`. Arguments: `EPROM`, optional
`OUTPUT_FILE`. Options `-f/--force`, `-a/--address`, `-s/--size`. Writes a raw binary of exactly
`memory-size` bytes when no `-a`/`-s` is given.

**`firestarter dev read <chip>`** — `cli_handlers.py:1344-1372`. **No output-file argument at all**;
prints a hexdump to console via `hexdump()`, and `size_str` defaults to `"256"`. CONTEXT is correct:
it is not a read-back path. (It is registered *ungated*, outside the `_DEV_TOOLS_ENABLED` blocks —
consistent with the channel split keeping `dev read` and `dev test` on stable.)

**`firestarter dev consistency-check <chip> --runs N --output-dir DIR`** — exists on this branch,
`cli_handlers.py:1496-1583`, and is **available in this devcontainer** [VERIFIED: `firestarter dev consistency-check --help` exits 0].

| Property | Value | Source |
|---|---|---|
| Gate | `if _DEV_TOOLS_ENABLED:` — `is_prerelease_build() or dev_tools_enabled_by_env()`, frozen at import | `cli_handlers.py:1289,1494`; `channel.py:144-162` |
| Gate status here | **enabled** — installed metadata `3.0.0b15`, source `3.0.0b20`; both PEP 440 pre-release | measured |
| Per-run file naming | `run_{i:02d}.bin` → `run_01.bin`, `run_02.bin`, `run_03.bin` | `eprom_operations.py:1058` |
| Default output dir | `firestarter-runs/consistency-check-<chip>-unknown-board-<TS>/` | `eprom_operations.py:1032-1037`, `DEFAULT_RUN_OUTPUT_DIR = "firestarter-runs"` |
| Minimum runs | `--runs < 2` → returns 2 (hw-error) before any serial I/O | `eprom_operations.py:1010-1016` |
| Exit code | **0 = PASS, 1 = FAIL (divergent SHAs), 2 = hardware/serial error** — *not* a bool | docstring `eprom_operations.py:991-1009` |
| Verdict block (pinned by a forward-compat regex test) | `Consistency check: PASS\|FAIL` / `Chip: … Board: unknown-board Port: …` / `Runs: N=…` / `Distinct SHAs: …` / `Output dir: …/` | `eprom_operations.py:1128-1134` |
| On FAIL, extra lines | `First divergence: offset 0x…` / `Total divergent bytes (run_1 vs run_2): …` / `First N divergent offsets: …` | `eprom_operations.py:1145-1165` |
| Other options | `--keep-files/--no-keep-files` (default keep), `--max-diffs` (10), `-q/--quiet`, `-f/--force`, `--read-settling`, `--read-strobe` | `cli_handlers.py:1498-1546` |

> **Artifact-location trap.** The meta repo's `.gitignore` ignores **`firestarter-runs/`**,
> **`consistency-check-*/`** and **`write-cycle-*/`**. Using the default output dir means the
> `run_NN.bin` evidence is **double-ignored and will not commit**. Pass an explicit
> `--output-dir .planning/phases/145-bench-validation/runs/cycleN/` with a directory name that does
> **not** start with `consistency-check-`. Committing `.bin` evidence has precedent: 208 `.bin`
> files are tracked under `.planning/`, including 23 W27C512 Leonardo `run_NN.bin` files at
> `.planning/v1.6/consistency-check-runs/`.

**D-06 oracle independence, stated precisely.** `verify_eprom` uses the **same**
`_main_phase_send_data` handler as `write` and the firmware performs the compare — it is a second
firmware-side pass, not an independent one. The genuinely independent oracle is
`read <chip> <file>` (firmware `CMD_READ` streams bytes) followed by a **host-side** `sha256sum`
compare against the source image. Record all three verdicts separately:

1. `write`'s own line — `Write to W27C512 successful (NN.NNs).` (`eprom_operations.py:1981-1984`)
2. `verify`'s own line — `Verify for W27C512 successful (NN.NNs).` (`eprom_operations.py:2017-2020`)
3. host SHA compare — `sha256sum imageN.bin readbackN.bin` must show the same digest

---

### RQ-4 (D-10) — Machine-counted intra-block bar motion: mechanism, wire shape, capture, and the arithmetic problem

**Where the frames come from.**

| Layer | Fact | Source |
|---|---|---|
| Firmware emit site | inside the per-byte loop, **before** the `0xFF`/already-matching skips | `eprom.cpp:399-402` |
| Guard | `#ifndef SERIAL_ON_IO` — **`leonardo` and `native` only**, compiled out on `uno`/`uno328pb` (BF-2) | `eprom.cpp:398,403` |
| Cadence | **time-keyed**, `EPROM_PROGRESS_EMIT_INTERVAL_MS` = **1000** | `include/eprom.h:85` |
| Cadence state | `uint32_t last_emit_ms = millis();` — a **function-local, re-initialised at the top of every block** | `eprom.cpp:326-328` |
| Payload | `LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS /*0xE0*/, addr, handle->mem_size)` — **absolute** chip address | `eprom.cpp:401` |
| Host handler | `_apply_write_progress` — parses `"absolute/total"`, applies `absolute - start_addr`, **ignores** total, sets `pbar.n` + `pbar.refresh()`, **never acks** | `eprom_operations.py:702-751` |
| Latch | first successfully-applied frame sets `firmware_drives_bar = True`, which stops the chunk-hand-off `progress.update()` | `eprom_operations.py:807-812, 876-889` |
| Bar format | `"{l_bar}{bar}| {n:#06x}/{total:#06x} bytes "` — tqdm, **stderr** | `eprom_operations.py:68, 385` |

**⚠ The arithmetic problem — the single most important planning finding in this section.**

A frame can only fire if a **single block's per-byte loop runs longer than 1000 ms**, because
`last_emit_ms` restarts at every block.

- A recorded, real 64 KiB W27C512 write on this exact board is **22.84 s**
  [CITED: `.planning/debug/resolved/write-empty-input-regression.md`] — and that figure *includes*
  the INIT blank check and erase.
- An in-tree firmware comment independently puts a typical `0x07` @100 µs 64 KiB write at **~32 s**
  (`eprom.cpp:492-495`).
- Leonardo blocks are 1024 B → **64 blocks** → **≈ 350–500 ms per block**, plus the final
  full-block verify pass and ~41 ms of serial transport ⇒ **≈ 400–700 ms**.

**⇒ At the database's 100 µs pulse, expect ZERO `0xE0` frames for the whole write.** The
`firmware_drives_bar` latch never engages; the bar is driven entirely by the chunk hand-off, and
**every frame lands on an exact multiple of 1024**. D-10's literal "more than one update inside a
single 1024-byte block" is not merely unlikely there — it is arithmetically out of reach.

Frames per block ≈ `floor(1024 × T_per_byte / 1000 ms)`, with `T_per_byte ≈ overhead + P` and
`overhead ≈ 250–350 µs`:

| `--pulse-us` | est. block time | est. frames/block | est. 64 KiB write | est. 4-block (4096 B) write | CAP-03 advertised budget |
|---|---|---|---|---|---|
| **100 (DB)** | ~0.4–0.5 s | **0** | ~25–35 s | ~2 s | 8 s |
| 1000 | ~1.3 s | 1 | ~85 s | ~5 s | 52 s |
| **2000** | ~2.3 s | **2** | ~150 s | ~9 s | 106 s |
| **4688** | ~5.1 s | **~5** | ~330 s | **~21 s** | **244 s** (> the 120 s fallback) |

**Recommended discharge, both halves of D-10 plus D-12, in ~25 s of bench time:** after cycle 3's
evidence is captured, run a **4096-byte** input at **`--pulse-us 4688`**:

```bash
firestarter write W27C512 img_4k_pulse.bin --pulse-us 4688
```
This crosses the **4687 µs** residual-gap threshold (`120 s / (25 × 1024) = 4687.5 µs`,
[CITED: `143-HOST-RECORD.md` §5 item 5]), so its advertised budget (244 s) exceeds the 120 s
fallback — it is the *sharpest* available CAP-03 proof, and it is where the intra-block frames
actually appear. `--pulse-us` also prints a mandatory default-visible provenance line
(`cli_handlers.py:678-690`) that belongs verbatim in the record:
`W27C512: --pulse-us 4688 overrides the database program pulse for this run (100 us -> 4688 us). This run's timing is NOT the database's.`

**Sequencing warning:** a short/`--address`-ranged write **still bulk-erases the whole chip** in
`eprom_write_init`. Run it only after cycle 3's read-back and SHA compare are complete.

**Capture mechanics — measured, not assumed.**

I reproduced `ClassProgressHandler`'s exact tqdm usage with stderr redirected to a **file (non-TTY)**:

```
$ python3 bar_probe.py 2> bar.err     # 327 bytes, 8 CR separators
  0%|          | 0x0000/0x10000 bytes
  2%|▏         | 0x05dc/0x10000 bytes
  4%|▎         | 0x0960/0x10000 bytes
  ...
```

| Risk | Verdict | Detail |
|---|---|---|
| tqdm auto-disables on non-TTY | **NO** — safe | `tqdm.tqdm(total=…, bar_format=…)` passes no `disable=None`, so it never auto-disables |
| Frames buffered / merged | **NO** — safe | frames are `\r`-separated, one write per display |
| `pbar.refresh()` suppressed by `mininterval` | **NO** — safe | `refresh()` forces a display; all 6 simulated `0xE0` refreshes appeared |
| `pbar.update()` suppressed by `mininterval` | **YES, real** | the `update(1024)` hand-off inside the default 0.1 s window produced **no frame**. Real hand-offs are ~400 ms apart so they will display — but do **not** assume a 1:1 frame:hand-off mapping |
| Output stream | **stderr** | tqdm's default; capture with `2>` |

**Recommended capture — no script needed for the raw half:**

```bash
firestarter -v write W27C512 imgN.bin > write_cycleN.stdout.log 2> write_cycleN.stderr.raw
```
Then count off-line:
```bash
tr '\r' '\n' < write_cycleN.stderr.raw \
  | grep -oE '0x[0-9a-f]+/0x10000 bytes' \
  | sed 's#/.*##' \
  | awk '{n=strtonum($1); printf "%d %d\n", n, int(n/1024)}' \
  | sort -n | uniq
```
- **Claim A (robust, reachable at any pulse):** *"at least one bar frame reported a position that is
  not a multiple of 1024"* — only a `0xE0` frame can produce that, since every chunk hand-off lands
  exactly on a 1024 boundary for a 65536-byte file on a 1024-byte-buffer board.
- **Claim B (D-10 as literally worded):** *"≥ 2 distinct positions inside the same `n // 1024`
  bucket"* — reachable **only** in the `--pulse-us` run.

**Two-bar discriminator.** The INIT-phase blank check *also* emits `MSG_DATA_PROGRESS`, at
`BLANK_CHECK_CHUNK_SIZE = 2048` (`memory.cpp:490, 450, 466-467`), and the operator record already
observed *"two distinct progress bars per 64 KB write (0x800-step blank-check during INIT, then
0x400-step write data during MAIN)"*. `ClassProgressHandler.start()` unconditionally closes and
re-creates the bar (`eprom_operations.py:382-385`), so a **newline** separates the two. **Count only
frames after the last bar restart**, or a 2048-step INIT frame will be miscounted as intra-block
write motion.

**Timestamps.** Plain shell redirection carries none. `ts` (moreutils) is **not installed**;
`script` (util-linux 2.41) and `stdbuf` are. `script` allocates a PTY, which is closer to what the
operator actually sees and supports `--log-timing`. If per-frame monotonic timestamps are wanted
without a PTY, a ~15-line Python `subprocess` reader writing `<monotonic>\t<chunk>` per read is the
cheapest route — that is bench tooling in the meta repo, **not** a source change to either sub-repo
(name it explicitly in the plan so the D-16 boundary stays legible).

---

### RQ-5 (D-18) — Reflash, image identity, and the version-string trap

**⚠ `firestarter fw --install` must NOT be used.** `firestarter_app/firestarter/firmware.py`
resolves a **GitHub release asset** (`_pick_asset` → `browser_download_url`, `_fetch_all_releases`)
and flashes that. The v1.31 firmware branch has **no release**, so `fw --install` would flash
`beta` — a different image. It also flashes the *attached* board regardless of `--board`
[CITED: prior operator finding]. `fw -f/--force` is a *different* force (install even if the
version matches) from the operation `--force` D-17 bans, but the whole command is off the table here.

**The correct route (Phase 99's, verbatim):**
```bash
cd /workspaces/firestarter
git rev-parse HEAD && git status --porcelain    # must be the commit under test, and EMPTY
pio run -t upload -e leonardo 2>&1 | tee /tmp/gsd-145/upload_leonardo.log
```

**Image identity facts to record:**

| Field | Value | How obtained |
|---|---|---|
| Firmware commit under test | `git rev-parse HEAD` in `/workspaces/firestarter` (tip today: `a594173`) | git |
| Working tree clean | `git status --porcelain` empty — **currently empty** [VERIFIED] | git |
| Flash bytes | **26906** (`Program: 26906 bytes`), RAM **2014** | `pio run -e leonardo --target size` [VERIFIED this session] |
| Matches `size_baseline.json` | **yes** — leonardo `flash_used 26906`, `flash_total 28672`, `flash_free 1766`, `ram_used 2014` | `scripts/baseline/size_baseline.json` |
| avrdude verified byte count | expect **26906** in the upload log | upload log |
| Reported version string | **`3.0.0b17`** | `firestarter fw` |
| Board name | `leonardo` | `firestarter fw` |

**The trap, stated precisely.** `include/version.h` on the v1.31 branch is `#define VERSION "3.0.0b17"`
— **byte-identical to the branch base `3085084`** — while `origin/beta` is `"3.0.0b18"`. So:
- a correctly flashed v1.31 image reports a version that looks **older** than beta;
- and `3.0.0b17` cannot distinguish the v1.31 tip from anything since the fork.

Note the host *display* path does show the suffix (`firmware.py:190-209` splits the raw
`"<version>:<board>"` identity on `:`, so `Current firmware version: 3.0.0b17, for controller:
leonardo on port /dev/ttyACMn`). It is `_probe_port`'s **version gate** that truncates via
`re.match(r"[\d.x]+", identity)` (`serial_comm.py:866`). Either way the string is not an image
identifier — the **commit + the 26906 B avrdude count** are.

Note on PIO's `% Full`: `pio run` reports `26906 bytes (82.1% Full)` against the 32768 B part, while
`size_baseline.json`'s `flash_total 28672` (bootloader excluded) gives **93.8 %** and **1766 B** of
headroom. Both figures are correct; quote the one you name.

**144 H7 / D-16, discharged for free.** A phase that compiles nothing new cannot move flash. Record
the measured 26906 B against the baseline's 26906 B — delta **0 B** against a 0 B leonardo band.
Optional corroboration:
```bash
python3 scripts/check_size_baseline.py --policy merge05 \
  --baseline scripts/baseline/size_baseline_base01.json \
  --avr-log leonardo=/tmp/gsd-145/upload_leonardo.log
```
(the canonical MERGE-05 invocation, `scripts/check_size_baseline.py:74-78`).

**Leonardo upload note.** The Leonardo needs a 1200-baud touch reset and re-enumerates on a
*different* port during upload. If more than one ACM device is present, pass the port explicitly
(`pio run -t upload -e leonardo --upload-port /dev/ttyACMn`). The PlatformIO avrdude here is
**version 8.1** (`~/.platformio/packages/tool-avrdude/avrdude`), whose wording differs from the 6.3
wording in the Phase 99 log — **capture the full upload log and read the byte count out of it; do
not hard-code a grep pattern.**

---

### RQ-6 (D-15 / BENCH-03) — The machine-checked `support_status` proof

**Already true. Four independent legs, all measured this session.** [VERIFIED: executed in `/workspaces/firestarter_app`]

**Leg 1 — the D-15 mandated diff over the WHOLE milestone range.**
```bash
cd /workspaces/firestarter_app
git merge-base HEAD origin/beta            # -> 4d18b645ab18a2d2465f0f623062e9249eb24132  (confirms the base)
git diff 4d18b645..HEAD -- firestarter/data/chip_database.json    # -> EMPTY (no output, exit 0)
git diff --stat 4d18b645..HEAD -- firestarter/data/chip_database.json   # -> no rows
```
`4d18b645` ("Apply automatic changes") is confirmed as the merge-base with `origin/beta`, not merely
asserted. Diff is **empty**.

**Leg 2 — the generator inputs are also unchanged**, so there is no latent drift that would change
`support_status` on the next regeneration:
```bash
git diff --stat 4d18b645..HEAD -- tools/build_db.py tools/extra_chips.json tools/infoic.xml   # -> EMPTY
```

**Leg 3 — the mechanism lock.** `tools/check_no_community_support_status_write.py` is an AST gate
that DENIES any `support_status` **assignment target** in `firestarter/diagnostic_report.py` and
`tools/parse_devtest_issue.py`, fail-closed if either scan target is missing. The sole sanctioned
write locus is `tools/build_db.py:714`. It runs automatically under `pytest tests/` via
`tests/test_check_no_community_support_status_write.py` (no separate CI step). D-15's proof
*composes with* this; it does not duplicate it.
```bash
python3 tools/check_no_community_support_status_write.py; echo "exit=$?"
```

**Leg 4 — the value histogram, as a positive statement rather than an absence.** Compute at the tip
and quote verbatim:
```
total chips: 746
  supported: 736
  adapter-required: 9
  protocol-not-implemented: 1
sha256(chip_database.json) = 3befbaad7bbb88307abd94db0447ad78e847c40f3c96be7751f5b87a1e913479
```

**Honest caveat for the record.** `git diff 4d18b645..HEAD` contains **three** textual mentions of
`support_status`, and the record should name them so a reader grepping the range is not alarmed:
- `tests/golden/chip_database_field_inventory.json` — `"support_status": 746` (a per-key *occurrence
  count*, part of a new golden that pins field counts) and `"support_status"` in a key list;
- `tests/test_write_response_budget.py` — a docstring mentioning `` support_status: supported ``.

None is a change to any chip's value. Also worth stating: the **firmware repo carries no
`support_status` at all** (grep over `src/ include/ scripts/` → zero hits), so BENCH-03 is
single-repo by construction.

---

### RQ-7 (D-17) — The VPP guard: exact band, and the concrete pot target

`eprom_check_vpp` (`firestarter/src/proms/eprom.cpp:525-586`) asserts the HV route mask, waits
`delay(100)`, reads `rurp_read_voltage_mv()`, then:

| Condition | Comparison | Outcome (no `--force`) | Outcome with `--force` |
|---|---|---|---|
| Over | `vpp_mv > handle->vpp_mv + 500` | `MSG_ERR_VPP_HIGH` → **RESPONSE_CODE_ERROR, run aborts** | `MSG_WARN_VPP_HIGH`, proceeds |
| Under | `vpp_mv < handle->vpp_mv * 95 / 100` | `MSG_WARN_VPP_LOW` → **WARNING, proceeds** | same |
| Rev 0 board | `rurp_get_hardware_revision() == REVISION_0` | `MSG_WARN_REV0_VPP_UNSUPPORTED`, **check skipped entirely** | same |

For W27C512, `handle->vpp_mv = 12000`:

- **Hard ceiling (abort):** measured **> 12500 mV**
- **Under-voltage warning floor:** measured **< 11400 mV**
- **In-band:** `11400 ≤ v ≤ 12500` mV

**Concrete instruction for the operator (state once, wait, take ONE confirming read):**
> Adjust the VPP pot until `firestarter vpp` reads **between 11.9 V and 12.4 V** (aim ~12.0–12.2 V).
> Below 11.4 V the firmware warns and programs under-driven; above 12.5 V it hard-aborts and
> `--force` is not permitted this phase.

**Sampling the monitor — better than `timeout -s INT`.** `vpp` and `vpe` carry a **hidden**
`-t/--timeout SECONDS` option (`cli_handlers.py:945-955`). `_read_voltage_loop`
(`hardware.py:207-276`) exits cleanly after the deadline, prints a newline and returns True (exit 0):
```bash
firestarter vpp -t 5 2>&1 | tr '\r' '\n' | tail -3
```
The Phase-99 form `timeout -s INT 12 firestarter vpp` also works and is the recorded precedent —
either is fine, but `-t` is cleaner and gives a non-zero-exit-free capture. Output frames are
written with `\r` to **stdout** (`hardware.py:251`), so `tr '\r' '\n'` is needed to read them.

Reminder from the standing record: `vpp`/`vpe` are **monitors that do not route voltage to the
socket** — safe with a chip seated; a blank or `0x303` reading indicates a contact fault.

---

### RQ-8 (record shape + BENCH-02's prior-state numbers)

**Template: `.planning/phases/99-.../99-03-BENCH-LOG.md` (116 lines).** Its structure, which this
phase should mirror:

```
# Phase NNN — <chip> <protocol> Bench Log
> one-paragraph honesty preamble: "Nothing here is fabricated. A tooling-blocked
> reading is recorded as 'not measured' with reason."
**Session start / Operator / Driver**
## Gate 1 — Pre-spend bench discipline + firmware build + VPP  (identity TABLE)
   | Controller identity | Port | Hardware revision (reported) | Shield silkscreen (operator eyes-on)
   | Seated chip (operator confirmed) | R1 readback | R2 readback | Firmware version string (+caveat)
   | Firmware commit under test | Reflash proof (avrdude byte count) | VPP target | VPP confirmation read
   | `--force` used? |
   **Gate 1 verdict:** PASS/FAIL — <one sentence naming each cleared condition>
## Gate 2 — Live spend
   **Operator authorization:** "<verbatim quote>" (date)
   ### Methodology deviation (operator-driven, honest)   <- only if one occurred
   ### Baseline & payload SHAs   (a TABLE, digests kept out of the narrative)
   ### <each run, its own subsection, with the exact command line as the heading>
   ### <each measurement that was NOT taken, with its blocking reason>
   ### SAFE-01 source assertion  (which flags were and were not used)
## VERDICT: <PASS | DEFER | FAIL> — <one line>
   - positive findings / residual defect / carry-forward
**Session end:** (operator-witnessed; name)
```

Load-bearing conventions worth copying: the **command line is the subsection heading** (so a reader
can see the flags without trusting prose); SHAs live in a **table**, not inline; every not-measured
reading gets its own line naming the blocker; and `--force used? No` is a row in the identity table.

**The exact prior-state numbers D-02's two skip records must cite.**

`0x08` — AM27C020 (Phase 99, 2026-07-01, Leonardo + Rev 2.0, firmware commit `35706c2`):
- Write #1 `firestarter write AM27C020 writeA.bin -a 0x1da00 -b` → RC 1,
  `Failed to write memory, 0x01da00, retries: 20, bad bytes: 4`; read-back **60 / 64 bytes
  byte-exact**; the failing bytes were the **first 4** (`0x1da00`–`0x1da03`, stayed `0xFF`).
- Read stability between them: `dev consistency-check AM27C020 --runs 3` → **PASS, N=3, 1 distinct
  SHA** (`4b192bba…a418`) — the partial state is real and stable, not a read glitch.
- Write #2 `firestarter write AM27C020 writeA.bin -a 0x16600 -b` → RC 1,
  `bad bytes: 64`; read-back **0 / 64** — the entire region stayed `0xFF`.
- Idle VPP both before and after: **12.9–13.0 V**, Internal VCC 5.5 V, inside the 12.75 ± 0.25 band.
- **Program-window VPP at socket pin 1: NOT MEASURED** — the held-rail DMM proxy is tooling-blocked
  by DTR-reset-on-close. Program-window droop under load is the leading hypothesis, never
  instrumented.
- Verdict: **DEFER (fix-effective-but-unreliable)**, carried as **FUT-08**.
- Under D-14's taxonomy this shape is a **fail**, not a qualified pass — say so.

`0x0B` — M2716/M2732 (Phase 79, rail-corrected 2026-06-23, Leonardo + Rev 2.0, fw 3.0.0b8, chip-OUT,
pot at MAX, R1/R2 = 270000/44000):
- **VPE = 22.4 V (operator DMM, AUTHORITATIVE) / 23.9 V (firmware `firestarter vpe`)** — ~90 % of the
  rated 25 V.
- VPP on the same run: ~15–19 V (operator DMM) / **18.7 V** (firmware `firestarter vpp`, dropped path).
- Strict ≥ 25 V bar: **NOT CLEARED**. The bar was then **retired** by operator override (79-CONTEXT
  D-07); the 4 NMOS chips graduate `supported` **best-effort**, firmware warns under-voltage
  (22.4 V < 23.75 V = 95 % of 25 V) and proceeds; over-voltage stays blocked.
- Definitive proof (a real write + independent read-back SHA) is **plan 79-03, deferred until a
  physical chip is on hand**. Graduation parked exactly there.
- Caveat to carry: the firmware ADC measures the regulator **rail** (23.9 V), not the socket-delivered
  pin voltage (22.4 V DMM).

Both records must close with the literal sentence D-02 demands, e.g.:
> *This disposition is NOT inferred from the `0x07` result. No `0x08` measurement was taken this
> phase; the numbers above are Phase 99's, cited, not re-derived.*

---

### RQ-9 — Test-suite tripwires: where bench artifacts may and may not be written

**PROVEN EMPIRICALLY THIS SESSION.** I created one empty untracked file at
`/workspaces/firestarter/ZZZ_p145_probe.txt`, ran both suites, and removed it:

| Suite | Result with the probe file | Result without |
|---|---|---|
| `firestarter_app`: `test_py32_flash_map_host.py`, `test_cap03_ack_layout_parity.py`, `test_py32_asset_name_host.py` | **4 failed, 34 passed** | 38 passed |
| `firestarter`: `test_flash_path_record_sync.py`, `test_trace_segment_exhaustiveness_v131.py`, `test_requirement_case_mapping_v131.py` | **5 failed, 56 passed** | 61 passed |

**Nine assertion sites, all of the form `_git_porcelain(<firmware repo root>) == ""`:**

| Repo | File:line |
|---|---|
| firestarter | `tests/test_flash_path_record_sync.py:1247` |
| firestarter | `tests/test_trace_segment_exhaustiveness_v131.py:1070`, `:1184` |
| firestarter | `tests/test_requirement_case_mapping_v131.py:753`, `:802` |
| firestarter_app | `tests/test_py32_flash_map_host.py:391` |
| firestarter_app | `tests/test_cap03_ack_layout_parity.py:746`, `:786` |
| firestarter_app | `tests/test_py32_asset_name_host.py:323` |

(One nuance worth correcting against the standing note: `test_flash_path_record_sync.py`'s
`test_dirty_tree_is_detected` deliberately does **not** assert cleanliness — *"a mid-plan working
tree is legitimately dirty"*. It is the five **planted-violation** legs above that do.)

**Where artifacts may go:**

| Location | Safe? | Why |
|---|---|---|
| `/workspaces/firestarter/**` (any new untracked file) | **NO — 9 tests RED** | proven above |
| `/workspaces/firestarter/.pio/**` | yes | `.pio` is gitignored (firmware `.gitignore:1`); verified — the `pio run` I did this session left porcelain empty |
| `/workspaces/firestarter/**/*.bin` | technically ignored (`*.bin`) but **do not** | ignored today; one `.gitignore` change and it becomes a landmine |
| `/workspaces/firestarter_app/**` | yes, no self-porcelain assertion exists | the host repo already carries 8 untracked entries and the suite is green; host `.gitignore` also ignores `*.bin` |
| `/workspaces/.planning/phases/145-bench-validation/**` | **yes — the recommended home** | meta repo, no porcelain gate; `.bin` under `.planning/` is tracked by precedent (208 files) |
| `/tmp/gsd-145/**` | yes | for raw build/upload logs not worth committing |

Two meta-repo `.gitignore` rules to route around (see RQ-3): **`firestarter-runs/`**,
**`consistency-check-*/`**, **`write-cycle-*/`** are ignored, so name the evidence directory
something else. `/*.bin` is root-only and does not affect the phase directory.

**Baselines established this session (quote these if a later run regresses):**
- `firestarter`: `pytest tests/ -q` → **312 passed in 17.29 s**
- `firestarter_app` (the 3 sibling-porcelain modules): **38 passed**
- `firestarter` porcelain: **empty**; `firestarter_app` porcelain: 8 pre-existing untracked entries
  (`.coverage`, `.planning/config.json`, `SECURITY.md`, 4 datasheets, `write_test_port.sh`).

> Use `-o addopts=""` when running `pytest -q`: the repo's `addopts` is `-ra -q` and doubling `-q`
> suppresses the count line.

---

## Standard Stack

This phase installs **nothing**. The stack is the tooling already present.

### Core

| Tool | Version | Purpose | Why standard |
|------|---------|---------|--------------|
| `firestarter` CLI | source `3.0.0b20`, dist-info `3.0.0b15`, **editable install of `/workspaces/firestarter_app`** | drives every serial operation | the host under test; editable, so the milestone-branch code runs |
| PlatformIO Core | **6.1.19** | builds + uploads the firmware image | the only route that flashes the tree under test (RQ-5) |
| avrdude (PIO-bundled) | **8.1** at `~/.platformio/packages/tool-avrdude/avrdude` | the actual flash write + verify | invoked by `pio run -t upload` |
| `pytest` | 9.1.1 | the two tripwire suites | already the house gate |
| `git` | present | BENCH-03's diff, the porcelain gates | — |
| `sha256sum` / `python3 hashlib` | present | D-06's independent oracle | the Phase-99 `SHA256SUMS.txt` pattern |

### Supporting

| Tool | Present? | Purpose |
|---|---|---|
| `script` (util-linux 2.41) | ✓ | PTY-backed capture with `--log-timing` if per-frame timestamps are wanted |
| `stdbuf` | ✓ | unbuffering, if ever needed |
| `ts` (moreutils) | **✗ not installed** | would be line-based anyway — the bar uses `\r`, so `ts` is the wrong tool regardless |
| `tr` / `awk` / `grep` | ✓ | frame extraction from the raw stderr capture |

### Alternatives Considered

| Instead of | Could use | Tradeoff |
|---|---|---|
| `pio run -t upload -e leonardo` | `firestarter fw --install` | **Wrong image** — pulls a GitHub release; the v1.31 branch has none (RQ-5) |
| custom address-stamped generator | `tools/gen_test_image.py` | zero new code, but a mismatch is not decodable to a source address (RQ-2) |
| `firestarter vpp -t 5` | `timeout -s INT 5 firestarter vpp` | both work; `-t` exits 0 cleanly, `timeout -s INT` is the Phase-99 precedent |
| `dev consistency-check` | three manual `read` + `sha256sum` calls | `consistency-check` gives a 3-way exit code and a pinned verdict block; manual gives full control over filenames |

**Installation:** none. No `pip install`, no `npm install`, no package added to any manifest.

---

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** D-16 forbids source changes and no
manifest is touched. `slopcheck` was therefore not run and no package appears in any recommendation.

If the planner introduces any dependency (it should not), the Package Legitimacy Gate must run
first and every package must be gated behind a `checkpoint:human-verify` task.

---

## Architecture Patterns

### The bench run, as data flow

```
                     ┌─────────────────────────────────────────────┐
  OPERATOR (physical) │ seat chip · read silkscreen · adjust pot ·  │
                      │ DMM · eyes-on bar confirmation              │
                      └───────────────┬─────────────────────────────┘
                                      │ (gates: human-action / human-verify)
                                      ▼
  GATE 0  (no hardware) ── BENCH-03 diff ──▶ verbatim git output ──┐
          ├── generate img1/img2/img3 ──▶ SHA256SUMS.txt           │
          └── write both BENCH-02 skip records                     │
                                      │                            │
                                      ▼                            │
  GATE 1  git rev-parse HEAD ─▶ pio run -t upload -e leonardo ─▶ upload log (avrdude bytes)
          firestarter fw   ─▶ controller/port/version              │
          firestarter hw   ─▶ reported revision                    │
          firestarter config ─▶ R1/R2                              │
          firestarter id W27C512 ─▶ chip-id 0xDA08 (fails safe)    │
          firestarter vpp -t 5 ─▶ ONE confirming read, 11.9–12.4 V │
          firestarter erase W27C512 -b ─▶ D-03 pre-flight          │
                                      │                            │
                          [operator authorization: verbatim quote] │
                                      ▼                            ▼
  GATE 2  for cycle in 1..3:                                  145-BENCH-LOG.md
            firestarter -v write W27C512 imgN.bin  2> stderr.raw   (identity table
              └─ INIT: check VPP → chip-id → ERASE → blank-check    · authorized spend
              └─ MAIN: 64 × 1024 B blocks, per-byte pulse→verify    · per-gate verdict
              └─ END : firmware VERIFY_PER_PULSE_PLUS_FINAL         · honest "not measured")
            firestarter verify W27C512 imgN.bin      ── oracle 1b        │
            firestarter read   W27C512 readbackN.bin ── oracle 2 ──┐     │
            sha256sum imgN.bin readbackN.bin  ─── host-side compare┘     │
            firestarter dev consistency-check W27C512 --runs 3 \          │
                 --output-dir .planning/.../runs/cycleN   ── D-07 ───────┘
                                      │
                                      ▼
  GATE 3  firestarter write W27C512 img_4k.bin --pulse-us 4688   (~21 s, 4 blocks)
            └─ D-10 machine half (≥2 frames/block) + D-12 --pulse-us-on-silicon
               + the >4687 µs CAP-03 budget-mechanism proof
```

### Recommended artifact layout

```
.planning/phases/145-bench-validation/
├── 145-BENCH-LOG.md              # the gated record (99-03 shape)
├── SHA256SUMS.txt                # every image + every read-back, one place
├── images/
│   ├── img1.bin  img2.bin  img3.bin  img_4k_pulse.bin
│   └── gen_addr_image.py         # 4-line generator (bench tooling, NOT sub-repo source)
├── runs/
│   ├── cycle1/ run_01.bin run_02.bin run_03.bin       # explicit --output-dir (NOT "consistency-check-*")
│   ├── cycle2/ …
│   └── cycle3/ …
├── logs/
│   ├── write_cycleN.stdout.log   write_cycleN.stderr.raw
│   ├── verify_cycleN.log         read_cycleN.log
│   └── pulse4688.stderr.raw
└── readbacks/ readback1.bin readback2.bin readback3.bin
```
Raw build/upload logs → `/tmp/gsd-145/` (not evidence worth committing; the byte count is quoted in
the record).

### Pattern 1: Gate 0 before any silicon

**What:** finish BENCH-02 and BENCH-03 completely, and generate + hash all four images, before the
board is even attached.
**When:** always in this phase.
**Why:** D-13 halts the phase on the first genuine `0x07` failure. If BENCH-02/03 are still
unwritten at that point, a halt costs two requirements that never needed hardware. BENCH-03 is
already provably true (RQ-6) and BENCH-02 is pure record-writing (RQ-8).

### Pattern 2: Command line as evidence heading

```markdown
### Cycle 2 — `firestarter -v write W27C512 img2.bin`
- exit: 0
- host line: `Write to W27C512 successful (28.31s).`
- `--force` used? **No** (visible in the heading)
```
From `99-03-BENCH-LOG.md`. A reader can audit the flags without trusting narrative — which is the
whole point of `--force used? No` being load-bearing (D-17).

### Pattern 3: Two-outcome discipline (D-14)

Every measurement lands in exactly one of: **validated** / **skipped-with-reason** / **fail**. Never
"inconclusive", never "partial". A `write` that reports `bad bytes: N` for any N > 0 is a **fail**
that triggers D-13, not a qualified pass.

### Anti-Patterns to Avoid

- **`write -b`.** Since Phase 92, `-b` skips only the blank check and the erase still runs — but the
  historical footgun is exactly what this milestone exists not to repeat, and `--skip-erase` (which
  sets `FLAG_SKIP_ERASE`) is the real hazard. Use neither.
- **`--force` anywhere on an operation.** D-17. A guard firing is a pre-flight fault.
- **`fw --install`.** Flashes a GitHub release, not the tree under test (RQ-5).
- **Default `--output-dir` on `dev consistency-check`.** Lands in a double-gitignored path (RQ-3).
- **Writing anything untracked into `/workspaces/firestarter`.** 9 tests RED (RQ-9).
- **A live VPP monitor loop while the operator turns the pot.** Standing operator preference: state
  the target, wait, take ONE confirming read.
- **Inferring the `0x08` or `0x0B` disposition from the `0x07` result.** BENCH-02's wording forbids
  it and D-02 requires an explicit denial sentence.
- **Reporting `3.0.0b17` as proof the right image is flashed.** It is identical to the fork point
  (RQ-5).

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Read-stability over N runs | a loop of `read` + `sha256sum` | `firestarter dev consistency-check --runs 3 --output-dir …` | 3-way exit code (0/1/2 — hw-error ≠ FAIL), a verdict block pinned by a forward-compat regex test, first-divergence offset reporting, and it reuses the production read path verbatim by design |
| Flashing the image under test | an avrdude invocation by hand | `pio run -t upload -e leonardo` | resolves the Leonardo 1200-baud touch reset, the right MCU/programmer/config, and emits the byte count in a log |
| Firmware size/headroom check | parsing `pio` output yourself | `scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log leonardo=…` | it *is* the MERGE-05 mechanism 144 H7 armed; a hand-rolled compare would not be the gate |
| `support_status` write prevention | a grep | `tools/check_no_community_support_status_write.py` | AST-based, fail-closed on a missing scan target, already wired into `pytest tests/` |
| Per-run progress capture | patching the host to log frames | plain `2>` redirection of the existing tqdm stderr | D-16 forbids source changes; the frames are already on stderr in a parseable form (RQ-4) |
| A "did the erase happen" probe | a bespoke erase-then-blank-check ritual | D-05's three-image sequence | 99.8 % of cycle-1→2 bytes need a `0→1` transition; a PASS *is* the proof (RQ-2) |

**Key insight:** every capability this phase needs already shipped and is already gated by a test.
Anything you find yourself writing is either bench glue (fine, in the meta repo) or a D-16 violation
(stop and report per D-13).

---

## Runtime State Inventory

> Not a rename/refactor phase, but the analogous question — *what state survives outside the files
> we control?* — is load-bearing on a bench. Every category answered explicitly.

| Category | Items found | Action required |
|---|---|---|
| **Stored data (on-chip)** | The W27C512's current 65536-byte content is unknown and will be **bulk-erased** by the first `write` (or by the D-03 pre-flight `erase`). Prior W27C512 read baselines exist at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-*` (23 tracked `run_NN.bin`) and are **ring-fenced GATE-1.8d evidence** — they are *not* comparable to this phase's read-backs (different chip content) and must not be overwritten. | Operator confirms the part is expendable before Gate 1. Do not touch `.planning/v1.6/`. |
| **Live host config** | `~/.firestarter/config.json` persists the last-used `port`. `find_and_connect` tries it **first**, then falls through to a port scan — so `-p` *prefers*, it does not *pin*. A saved port also makes two host tests (`test_no_programmer_found_*`) go RED. | Pass `-p /dev/ttyACMn` per invocation (`config_manager.set_value(..., persist=False)` — does not save). Record the port the CLI actually reports, from `firestarter fw`'s `on port …`. |
| **On-board persistent state** | Arduino EEPROM `rurp_configuration_t`: R1/R2 calibration and the `hw_revision` override. Survives a reflash. The `hw_revision` byte **cannot distinguish Rev 2.0 from 2.2 from modified Rev 0** (D-01). | Read R1/R2 via `firestarter config` and record. Board revision comes from operator eyes-on silkscreen only. |
| **Flashed image** | Whatever is on the Leonardo now is unknown. A pre-CAP-02 v1.31 image **cannot connect at all** (BF-1); a released beta ≥ b18 connects but lacks CAP-03. | Mandatory reflash (D-18). Identify by commit + 26906 B, never by `3.0.0b17`. |
| **Build artifacts** | `/workspaces/firestarter/.pio/` — gitignored, already populated by this session's `pio run -e leonardo --target size` (porcelain verified empty afterwards). | None. Do not `rm -rf` it; a rebuild is ~1 s warm. |
| **Ports** | `/dev/ttyACM*`: **none attached right now** (`serial.tools.list_ports` reports only `/dev/ttyS0..3`). Numbering shuffles across replug; the Leonardo re-enumerates on a different port during upload. | Verify `controller:`/port identity per task, never carry it forward (D-19). |

---

## Common Pitfalls

### Pitfall 1: Planning D-10 around the database pulse
**What goes wrong:** the plan specifies "count ≥2 progress updates per 1024-byte block" during the
three required 100 µs cycles; the capture shows every frame on an exact multiple of 1024 and the
claim cannot be made.
**Why:** `EPROM_PROGRESS_EMIT_INTERVAL_MS = 1000` with a per-block-reinitialised `last_emit_ms`,
against a ~400–700 ms block (RQ-4).
**Avoid:** make Claim A (`n mod 1024 ≠ 0`) the DB-pulse claim, and put Claim B in a dedicated
`--pulse-us 4688` run.
**Warning sign:** `grep -c` over extracted `n` values returns exactly 64 and all are multiples of 1024.

### Pitfall 2: `fw --install` as the reflash
**What goes wrong:** the board ends up running a **beta** image; every subsequent measurement is
attributed to the wrong build.
**Why:** `firmware.py` resolves a GitHub release asset; the v1.31 branch has no release.
**Avoid:** `pio run -t upload -e leonardo` only.
**Warning sign:** the reported version is `3.0.0b18` or later (beta), or the avrdude byte count ≠ 26906.

### Pitfall 3: Treating `3.0.0b17` as proof
**What goes wrong:** the record claims the v1.31 image is under test on the strength of a version
string that is byte-identical to the branch's own fork point.
**Avoid:** record commit + clean tree + 26906 B avrdude count, all three, as separate rows.

### Pitfall 4: A bench artifact inside the firmware checkout
**What goes wrong:** 5 firmware tests and 4 host tests go RED; a later "suite green" claim is false.
**Avoid:** artifacts under `.planning/phases/145-bench-validation/` or `/tmp/gsd-145/`. Run
`git -C /workspaces/firestarter status --porcelain` and assert empty **immediately before** any
suite run.

### Pitfall 5: Default `--output-dir` on `dev consistency-check`
**What goes wrong:** `run_NN.bin` evidence lands in `firestarter-runs/consistency-check-…/`, matched
by **two** meta `.gitignore` rules, and silently never commits.
**Avoid:** explicit `--output-dir` with a name not starting with `consistency-check-`.

### Pitfall 6: Confusing INIT blank-check frames with intra-block write frames
**What goes wrong:** the 32 blank-check frames (2048-byte steps, during INIT) inflate the count and
produce a false "intra-block motion" claim.
**Avoid:** count only frames after the last bar restart (`ClassProgressHandler.start()` closes and
re-creates the bar, leaving a newline in the capture).

### Pitfall 7: `-b` polarity is inverted between `write` and `erase`
**What goes wrong:** `erase -b` is read as "skip the blank check" and the pre-flight proves less
than intended.
**Fact:** `write -b`/`--no-blank-check` **removes** the blank check; `erase -b`/`--blank-check`
**adds** one. Both polarities coexist verbatim from the argparse era (documented in both docstrings).

### Pitfall 8: Group options placed after the subcommand
**What goes wrong:** `firestarter write W27C512 img.bin -v -p /dev/ttyACM0` → Click error; `-v` and
`-p` live on the **group**.
**Correct:** `firestarter -v -p /dev/ttyACM0 write W27C512 img.bin`

### Pitfall 9: Chasing the CAP-03 budget instead of receiving it
**What goes wrong:** effort spent trying to observe the advertised `write_block_budget_s`.
**Fact:** nothing logs it (`serial_comm.py:429-441` decodes it silently). D-11's evidence is simply
*that the write completed* — the budget held. For W27C512 @100 µs on a 1024 B block the advertised
value is **8 s** [computed from `eprom_block_budget_s`: `25 × 100 µs = 2500 µs/byte`;
`ceil(2500 × 1024 / 1e6) = 3 s`; `3 × 2 + 2 = 8 s`]; the 120 s fallback is
`WRITE_BLOCK_TIMEOUT_FALLBACK_S`.

### Pitfall 10: `pytest -q` hiding the count line
**Fact:** the repos' `addopts` is `-ra -q`; doubling `-q` suppresses the summary count. Use
`-o addopts=""`.

---

## Code Examples

All commands below are verified against the shipped source. **None uses `--force`. None uses `-b` or
`--skip-erase` on `write`.**

### Gate 0 — BENCH-03 (no hardware)
```bash
cd /workspaces/firestarter_app
git merge-base HEAD origin/beta                                   # expect 4d18b645ab18a2d2465f0f623062e9249eb24132
git diff 4d18b645..HEAD -- firestarter/data/chip_database.json    # expect EMPTY
git diff --stat 4d18b645..HEAD -- tools/build_db.py tools/extra_chips.json tools/infoic.xml   # expect EMPTY
python3 tools/check_no_community_support_status_write.py; echo "exit=$?"
sha256sum firestarter/data/chip_database.json                     # expect 3befbaad7bbb…13479
python3 - <<'PY'
import json, collections
d = json.load(open('firestarter/data/chip_database.json'))
c = collections.Counter(ic.get('support_status') for ics in d.values() for ic in ics)
print('total chips:', sum(c.values())); [print(f'  {k}: {v}') for k, v in c.most_common()]
PY
```

### Gate 0 — generate the four images
```bash
mkdir -p .planning/phases/145-bench-validation/images
python3 - <<'PY'
import hashlib, pathlib
def img(size, mask):
    b = bytearray(size)
    for n in range(size):
        b[n] = ((n >> 8) & 0xFF if (n & 1) else n & 0xFF) ^ mask
    return bytes(b)
out = pathlib.Path('.planning/phases/145-bench-validation/images')
for name, size, mask in (('img1.bin',65536,0x00), ('img2.bin',65536,0xFF),
                         ('img3.bin',65536,0x5A), ('img_4k_pulse.bin',4096,0x3C)):
    d = img(size, mask); (out/name).write_bytes(d)
    print(f'{hashlib.sha256(d).hexdigest()}  {name}  ({len(d)} B, mask 0x{mask:02X})')
PY
```
Expected 64 KiB digests (reproducible):
`img1` `f72489604bfe917db7ee505e4d674576b2905a418e8dc55372b78dcab3e34e3a` ·
`img2` `b566c7a0319cc37051ec9c92bc1faef81f75e3740c7c6c8864778a549624fd96` ·
`img3` `74c359c8d8668fdc5778270d61cc3fbef55a1027999f20c5798a54bf0f6aea01`

### Gate 1 — image identity and reflash
```bash
cd /workspaces/firestarter
git rev-parse HEAD; git status --porcelain                        # commit under test; MUST be empty
pio run -e leonardo --target size                                 # expect Program: 26906 / Data: 2014
mkdir -p /tmp/gsd-145
pio run -t upload -e leonardo 2>&1 | tee /tmp/gsd-145/upload_leonardo.log
grep -iE '[0-9]{4,} bytes' /tmp/gsd-145/upload_leonardo.log       # avrdude 8.1 wording differs from 6.3 — read the log
```

### Gate 1 — bench identity (each with `-p` and the reported port recorded)
```bash
firestarter -p /dev/ttyACM0 fw          # controller identity, port, version string (3.0.0b17 expected)
firestarter -p /dev/ttyACM0 hw          # reported hardware revision (NOT authoritative for 2.0 vs 2.2)
firestarter -p /dev/ttyACM0 config      # R1/R2 readback
firestarter -p /dev/ttyACM0 id W27C512  # chip-id gate; fails safe on the ST 0x203D part
firestarter -p /dev/ttyACM0 vpp -t 5 2>&1 | tr '\r' '\n' | tail -3   # ONE confirming read
```

### Gate 1 — D-03 pre-flight (also leaves the chip blank for cycle 1)
```bash
firestarter -p /dev/ttyACM0 erase W27C512 -b    # -b here ADDS a post-erase blank check
echo "exit=$?"                                   # 0 == erase supported AND physically effective
firestarter -p /dev/ttyACM0 blank W27C512        # optional second confirmation
```

### Gate 2 — one cycle (repeat for N = 1, 2, 3 with imgN.bin)
```bash
P=/dev/ttyACM0 ; N=1 ; D=.planning/phases/145-bench-validation
firestarter -v -p $P write  W27C512 $D/images/img$N.bin \
    >  $D/logs/write_cycle$N.stdout.log  2> $D/logs/write_cycle$N.stderr.raw ; echo "write exit=$?"
firestarter    -p $P verify W27C512 $D/images/img$N.bin 2>&1 | tee $D/logs/verify_cycle$N.log
firestarter    -p $P read   W27C512 $D/readbacks/readback$N.bin 2>&1 | tee $D/logs/read_cycle$N.log
sha256sum $D/images/img$N.bin $D/readbacks/readback$N.bin | tee -a $D/SHA256SUMS.txt
firestarter    -p $P dev consistency-check W27C512 --runs 3 \
    --output-dir $D/runs/cycle$N 2>&1 | tee $D/logs/consistency_cycle$N.log ; echo "cc exit=$?"
```
`dev consistency-check` exit: **0 PASS · 1 FAIL (divergent SHAs) · 2 hardware/serial error.**

### Gate 2 — frame extraction for D-10
```bash
N=1 ; D=.planning/phases/145-bench-validation
# split the two bars; keep only the write bar (everything after the last bar restart)
tr '\r' '\n' < $D/logs/write_cycle$N.stderr.raw | awk '/bytes $/{print}' > /tmp/gsd-145/frames_$N.txt
grep -oE '0x[0-9a-f]+/0x10000' /tmp/gsd-145/frames_$N.txt | sed 's#/.*##' \
  | awk '{n=strtonum($1); printf "%d\t%d\t%s\n", n, int(n/1024), (n%1024==0 ? "boundary" : "INTRA-BLOCK")}' \
  | sort -n -u | tee /tmp/gsd-145/positions_$N.tsv
echo "intra-block frames: $(grep -c INTRA-BLOCK /tmp/gsd-145/positions_$N.tsv)"
awk -F'\t' '{c[$2]++} END{for (b in c) if (c[b] > 1) print "block", b, "has", c[b], "updates"}' \
  /tmp/gsd-145/positions_$N.tsv
```

### Gate 3 — D-10 Claim B + D-12 in one ~21 s run
```bash
firestarter -v -p /dev/ttyACM0 write W27C512 \
    .planning/phases/145-bench-validation/images/img_4k_pulse.bin --pulse-us 4688 \
    >  .planning/phases/145-bench-validation/logs/pulse4688.stdout.log \
    2> .planning/phases/145-bench-validation/logs/pulse4688.stderr.raw
```
Expected stdout provenance line (record verbatim):
`W27C512: --pulse-us 4688 overrides the database program pulse for this run (100 us -> 4688 us). This run's timing is NOT the database's.`
Then re-run the frame extraction — expect **~5 updates per block on all 4 blocks**.

### Suite hygiene, immediately before any pytest run
```bash
git -C /workspaces/firestarter status --porcelain     # MUST be empty or 9 tests go RED
cd /workspaces/firestarter     && python3 -m pytest tests/ -q -o addopts=""   # baseline: 312 passed
cd /workspaces/firestarter_app && python3 -m pytest tests/ -q -o addopts=""
```

---

## State of the Art

| Old belief (carried in the phase context / record) | Current reality | When it changed | Impact on the plan |
|---|---|---|---|
| `firestarter erase W27C512` → `ERROR: Not supported`; erase capability unresolved | `FLAG_CAN_ERASE` is set (`flags=0x02`); plain `write` erases; bench-proven in Phase 77 and Phase 91 | v1.11 `cca7d62` (decode) → v1.14 Phase 77 (flag derivation + bench proof) | D-03's fallback becomes a contingency, not a branch point |
| "the note says firmware-supported, operator-bench-pending" | that note is the **v1.11 todo's own closing caveat**, superseded twice since | v1.14 / v1.16 | quote the supersession chain in the record |
| `fw --install` is a reflash route | it downloads a GitHub release asset; the v1.31 branch has none | always true; newly relevant | use `pio run -t upload -e leonardo` |
| version string cannot show a prerelease suffix | the **gate** truncates (`[\d.x]+`); the `fw` **display** shows `3.0.0b17` in full — but `3.0.0b17` is identical to the fork point, so it identifies nothing anyway | 143/144 records | record commit + byte count |
| intra-block progress "should" appear on a normal write | time-keyed at 1000 ms with a per-block reset; a DB-pulse block is ~0.4–0.7 s | Phase 143 (`eprom.cpp:399`) | D-10 needs a `--pulse-us` run |
| MERGE-05 leonardo band shows real headroom compliance | the **anchor moved** at Phase 144; delta 0 means the baseline was re-anchored to the v1.31 tip, not that growth stayed inside v1.24's band | Phase 144 D-11 | quote `deltas_vs_base01.leonardo.merge05_clause` verbatim rather than claiming compliance |

**Deprecated / superseded:**
- The `w27c512-eeprom-misclassification` todo — **resolved 2026-06-09**, now in
  `.planning/todos/completed/`.
- Phase 24's `.planning/v1.5-BENCH-RESULTS.md` row 10 ("EEPROM electrical erase ✗ NOT SUPPORTED") —
  superseded; do not cite it as current.

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| PlatformIO Core | reflash (D-18), size check (D-16) | ✓ | 6.1.19 | none needed |
| avrdude (PIO-bundled) | flash write + verify | ✓ | **8.1** at `~/.platformio/packages/tool-avrdude/avrdude` (a 6.3 copy also present) | — |
| `avrdude` on PATH | not used | ✓ | `/usr/bin/avrdude` | not the one PIO invokes |
| `firestarter` CLI | every serial operation | ✓ | editable install of `/workspaces/firestarter_app` (dist-info `3.0.0b15`, source `3.0.0b20`) | `pip install -e .` if it drifts |
| `dev consistency-check` gate | D-07 | ✓ enabled | pre-release build ⇒ `is_dev_tools_enabled() == True` | `FIRESTARTER_DEV_TOOLS=1` |
| pytest | tripwire suites | ✓ | 9.1.1 | — |
| git | BENCH-03, porcelain gates | ✓ | — | — |
| `script` (util-linux) | optional timestamped capture | ✓ | 2.41 | plain `2>` redirection |
| `stdbuf` | optional | ✓ | coreutils | — |
| `ts` (moreutils) | would-be timestamping | **✗** | — | wrong tool anyway (line-based; the bar uses `\r`) — use `script --log-timing` or a ~15-line Python reader |
| **`/dev/ttyACM*` (the board)** | **all of Gates 1–3** | **✗ NOT ATTACHED** | — | **none — hard blocker** |
| W27C512 (Winbond, `0xDA08`) | BENCH-01 | operator-held | — | **none** — TMS27C512 is explicitly not to be spent (D-01) |
| RURP Rev 2.0 shield | BENCH-01 comparability | operator-held | — | Rev 2.2 would break comparability with Phases 79/99 |
| AM27C020 | BENCH-02 `0x08` | **✗ not on bench** | — | **skip-with-reason** (D-02) |
| M2716 / M2732 | BENCH-02 `0x0B` | **✗ not on bench** | — | **skip-with-reason** (D-02) |
| DMM | operator VPP/VPE readings | operator-held | — | firmware ADC read via `vpp`/`vpe`, recorded as such |

**Missing with no fallback (blocking):** the attached Leonardo + seated W27C512 + Rev 2.0 shield.
Every Gate-1..3 task must sit behind a `checkpoint:human-action` that the operator clears by
attaching the board. `serial.tools.list_ports` currently reports only `/dev/ttyS0..3`.

**Missing with fallback:** `ts` (use `script --log-timing` or plain redirection); AM27C020 and
M2716/M2732 (recorded skips — this is the requirement-sanctioned path, not a workaround).

---

## Validation Architecture

`.planning/config.json` contains no `workflow.nyquist_validation` key ⇒ **treat as enabled**.

### Test framework

| Property | Value |
|---|---|
| Framework | pytest 9.1.1 (both sub-repos); PlatformIO Unity for the firmware native suites |
| Config file | **none** in `/workspaces/firestarter` (recorded house rule — no `conftest.py`, `pytest.ini`, `pyproject.toml`, `setup.cfg`, `tox.ini`); `firestarter_app` has `pyproject.toml` with `addopts = -ra -q` |
| Quick run (firmware) | `cd /workspaces/firestarter && python3 -m pytest tests/ -q -o addopts=""` — **17.3 s, 312 passed** |
| Quick run (host, tripwire subset) | `cd /workspaces/firestarter_app && python3 -m pytest tests/test_py32_flash_map_host.py tests/test_cap03_ack_layout_parity.py tests/test_py32_asset_name_host.py -q -o addopts=""` — **0.5 s, 38 passed** |
| Full suite | `python3 -m pytest tests/ -q -o addopts=""` in each sub-repo |
| Precondition | `git -C /workspaces/firestarter status --porcelain` **must be empty** — otherwise 9 tests RED (proven, RQ-9) |

**This phase adds no automated tests** — D-16 forbids source changes, and BENCH-01/02 are
irreducibly hardware- and operator-gated. The suites are run as **regression tripwires**, not as
requirement evidence.

### Phase requirements → validation map

| Req | Behaviour to prove | Type | Command / artifact | Exists? |
|---|---|---|---|---|
| **BENCH-01** | erase capability on the `0x07` path | hardware pre-flight | `firestarter erase W27C512 -b` → exit 0 | ✅ command exists |
| BENCH-01 | 64 KiB write completes, firmware verify passes | hardware | `firestarter -v write W27C512 imgN.bin` → exit 0 + `Write to W27C512 successful (…s).` | ✅ |
| BENCH-01 | second firmware-side compare | hardware | `firestarter verify W27C512 imgN.bin` → exit 0 | ✅ |
| BENCH-01 | **independent** oracle (D-06) | hardware + host | `firestarter read W27C512 readbackN.bin` then `sha256sum` equality against `imgN.bin` | ✅ |
| BENCH-01 | read stability per cycle (D-07) | hardware | `dev consistency-check W27C512 --runs 3 --output-dir …` → **exit 0**, `Distinct SHAs: 1` | ✅ |
| BENCH-01 | erase actually fired (D-03 corroboration) | derived | cycles 2 and 3 PASS while 99.8 % / 90.6 % of bytes require a `0→1` transition | ✅ arithmetic verified |
| BENCH-01 | 3/3 byte-exact on both oracles (D-09) | derived | all three cycles PASS on both oracle lines; any re-seat recorded twice | — |
| BENCH-01 | no `--force` (D-17) | source assertion | every recorded command line, quoted as its own subsection heading | ✅ |
| **BENCH-02** `0x08` | skip-with-reason naming the part + prior numbers | record | `145-BENCH-LOG.md` section citing 60/64, 0/64, FUT-08, and the explicit not-inferred sentence | ✅ numbers in RQ-8 |
| **BENCH-02** `0x0B` | same | record | section citing 22.4 V DMM / 23.9 V firmware at max pot, graduation parked | ✅ numbers in RQ-8 |
| **BENCH-03** | no `support_status` change across the whole v1.31 range | automated | `git diff 4d18b645..HEAD -- firestarter/data/chip_database.json` **empty** (verbatim) + generator-inputs diff empty + `check_no_community_support_status_write.py` exit 0 + the 736/9/1 histogram | ✅ **all four measured** |
| D-10 (143 H4) | intra-block bar motion, machine half | derived from capture | Claim A at DB pulse; **Claim B from the `--pulse-us 4688` run** | ✅ method verified |
| D-10 | operator eyes-on half | human-verify | operator confirms a smoothly moving bar, not an end-burst | — |
| D-11 (143 H4) | long write survives the advertised budget | free | the 64 KiB write completed at all | — |
| D-16 / 144 H7 | zero flash growth | automated | `pio run -e leonardo --target size` = **26906 / 2014**, equal to `size_baseline.json`; optional `check_size_baseline.py --policy merge05` | ✅ measured |
| D-12 (stretch) | `--pulse-us` on silicon above 4687 µs | hardware | the Gate-3 run; if not attempted, recorded as an **explicitly-not-discharged hand-off with no v1.31 owner** | ✅ |
| D-12 (stretch) | A1 per-pulse overhead | derived | `T_per_byte = elapsed_write / bytes`; `A1 ≈ T_per_byte − pulse_us`. Two runs at different `--pulse-us` over the same byte count cancel the fixed INIT/erase/transport cost: `(t₂ − t₁)/N` should equal `P₂ − P₁`. Record the error bars honestly (the reported elapsed includes the INIT blank check). | ✅ method defined |

### Sampling rate

- **Per gate:** the gate's own commands + `git -C /workspaces/firestarter status --porcelain` empty.
- **Per plan commit:** firmware `pytest tests/ -q -o addopts=""` (17 s) — cheap enough to run every time.
- **Phase gate:** both full suites green + firmware porcelain empty, immediately before
  `/gsd-verify-work`.

### Wave 0 gaps

- [ ] `.planning/phases/145-bench-validation/images/*.bin` + `SHA256SUMS.txt` — generated in Gate 0,
      before any hardware.
- [ ] `.planning/phases/145-bench-validation/145-BENCH-LOG.md` skeleton (99-03 gate structure) —
      authored in Gate 0 so a D-13 halt still lands a usable record.
- [ ] `runs/`, `logs/`, `readbacks/` directories with an explicit non-`consistency-check-*` naming.

*No test-framework install is needed; no test file is added.*

---

## Security Domain

`security_enforcement` is absent from `.planning/config.json` ⇒ treated as enabled. The classical
web ASVS categories do not map onto a bench phase that writes no code and exposes no network
surface; the honest mapping is below, with the *hardware*-safety controls that genuinely apply.

### Applicable ASVS categories

| ASVS category | Applies | Standard control |
|---|---|---|
| V2 Authentication | no | no auth surface — local serial only |
| V3 Session Management | no | no sessions |
| V4 Access Control | no | no multi-user surface |
| V5 Input Validation | **partial** | `--pulse-us` is bounded at Click parse time by `click.IntRange(1, 65535)` (exit 2 before any serial byte); the firmware independently refuses over-cap pulses with `MSG_ERR_PULSE_TOO_WIDE` before enabling high voltage |
| V6 Cryptography | **partial** | SHA-256 via `hashlib`/`sha256sum` — used as an integrity oracle, never hand-rolled |
| V12 Files & Resources | **yes** | artifacts written only to the meta repo / `/tmp`; never into the firmware checkout (RQ-9) |
| V14 Configuration | **yes** | `-p … persist=False` avoids mutating `~/.firestarter/config.json` |

### Hardware-safety threat patterns for this stack

| Pattern | Category | Standard mitigation |
|---|---|---|
| Over-voltage on VPP damaging the part | Physical damage | `eprom_check_vpp` hard-aborts above `vpp_mv + 500` (12500 mV for W27C512). **`--force` converts this abort into a warning — banned this phase (D-17).** |
| Wrong part seated (ST `0x203D` vs Winbond `0xDA08`) | Physical damage / false result | `eprom_generic_init` chip-id check aborts without `--force`; the ST part is 13 V and non-erasable. **Fails safe by design — this is exactly how the v1.18 P97 mix-up was caught.** |
| 12 V onto a 5 V pin | Physical damage | `tools/check_dispatch.py`'s structural guard (no `configure_eprom` chip on a pinout without a VPP pin) + the WARNING-5 override; unchanged this phase |
| Silent skip-erase producing "successful" with bad bytes | False green | `--skip-erase` and `write -b` both banned; the three-image sequence makes a no-op erase fail loudly |
| Flashing an unintended firmware image | Wrong-conclusion risk | `pio run -t upload` from a named, clean commit; 26906 B avrdude cross-check (RQ-5) |
| Stale/unknown image on the board | Wrong-conclusion risk | mandatory reflash (D-18); BF-1 means a pre-CAP-02 image cannot even connect |
| Auto-approval of an operator gate | Process | **no `--auto`, no `--chain`** (D-20); `autonomous: false` alone is not self-protecting |

**Explicit non-claim:** no supply-chain control applies here because no package is installed and no
manifest is touched.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | A 1024-byte block at the DB's 100 µs pulse takes **~400–700 ms**, so **zero** `0xE0` frames fire per block. Derived from a recorded 22.84 s 64 KiB W27C512 Leonardo write (pre-v1.31 firmware) and an in-tree ~32 s estimate — **not measured on the v1.31 per-byte loop**. `[ASSUMED]` | RQ-4 | If v1.31 is >2× slower, 1 frame/block appears at the DB pulse (still not 2). Mitigation: the Gate-3 `--pulse-us` run makes Claim B reachable either way, and the frame-extraction script reports the truth regardless. |
| A2 | Per-byte loop overhead is **~250–350 µs** (the basis for the `--pulse-us` frame table). `[ASSUMED]` | RQ-4 | The 4688 µs choice has ~5× margin over the 1-frame threshold; even a 3× error in the overhead estimate leaves ≥2 frames/block. |
| A3 | avrdude 8.1's upload log contains a readable "N bytes" figure equal to 26906. `[ASSUMED]` — I could not run an upload without a board, and 8.x wording differs from the 6.3 wording in the Phase-99 log. | RQ-5 | If the wording differs, the byte-count row must be filled from whatever the log actually says. Mitigation: capture the whole log and read it; do not hard-code a grep pattern. |
| A4 | The Leonardo currently on the operator's bench has *some* firmware; whether it connects at all is unknown. `[ASSUMED]` | RQ-5 | Reflash is mandatory regardless (D-18), so this cannot mislead. |
| A5 | The `firestarter` CLI's editable install still resolves to `/workspaces/firestarter_app` at bench time (dist-info says `3.0.0b15`, source `pyproject` says `3.0.0b20`). `[VERIFIED today]` but reinstallable drift is possible. | Environment | A stale metadata version does not affect behaviour (both are pre-release ⇒ dev tools enabled), but re-run `pip install -e .` if `firestarter --version` disagrees with the source. |
| A6 | The operator's W27C512 is expendable and its current content need not be preserved. `[ASSUMED]` | Runtime State | A pre-write full-chip `read` before the first erase costs ~15 s and removes the risk entirely — recommend it as a Gate-1 step. |
| A7 | The `--pulse-us 4688` short write is acceptable chip wear. `[ASSUMED]` | RQ-4 | It is one extra erase+program cycle on an electrically-erasable EEPROM (rated for many). Operator confirms at the Gate-3 authorization. |

---

## Open Questions (RESOLVED)

All five questions below were resolved during planning; each carries an inline
`**RESOLVED:**` marker naming the plan and task that adopted its recommendation. The question text itself is
unchanged from the research session.

1. **Does the v1.31 per-byte loop change the 64 KiB write duration materially?**
   - Known: 22.84 s recorded on this chip/board under the pre-v1.31 block loop; an in-tree comment
     estimates ~32 s for `0x07` @100 µs; the v1.31 loop adds a per-byte verify read *and* a final
     full-block verify pass, but skips `0xFF` and already-matching bytes.
   - Unclear: the exact v1.31 figure.
   - Recommendation: the plan records the wall-clock elapsed from cycle 1 as a **first-class
     measurement** (it is free — `Write to W27C512 successful (NN.NNs).`), and the frame extraction
     reports the true per-block frame count rather than asserting a predicted one.
   - **RESOLVED:** adopted. `145-05` Task 2 records cycle 1's elapsed seconds as a first-class measurement and
     `145-06` Tasks 1 and 2 do the same for cycles 2 and 3, with all three figures placed side by side and no
     comparative claim against earlier firmware (D-08).

2. **How many `0xE0` frames actually arrive at the DB pulse — 0 or 1 per block?**
   - Recommendation: do not pre-commit either number in the plan. State Claim A as the DB-pulse
     claim, let the extraction script report the count, and put Claim B in Gate 3.
   - **RESOLVED:** adopted. `145-05` Task 3 gives Claim A a measured verdict rather than a predicted one, with
     both `HOLDS` and `DOES NOT HOLD` pre-authorised as recorded outcomes; Claim B sits in Gate 3 (`145-07`).

3. **Should the pre-write chip content be preserved?**
   - Recommendation: one `firestarter read W27C512 prewrite.bin` before the first erase, hashed into
     `SHA256SUMS.txt` — Phase 99 did exactly this (`prewrite.bin`, `90cd45f5…7297`) and it later
     served as defer-branch evidence. Cheap insurance.
   - **RESOLVED:** adopted. `145-04` Task 1 captures `readbacks/prewrite.bin` and appends its digest to
     `SHA256SUMS.txt` before Task 2's erase authorization is even presented.

4. **Does the plan want the `run_NN.bin` binaries committed?**
   - Known: precedent exists (208 tracked `.bin` under `.planning/`, incl. 23 W27C512 Leonardo
     `run_NN.bin`); ~9 × 64 KiB ≈ 600 KB total.
   - Recommendation: commit them (they are the evidence D-07 rests on) under a non-ignored directory
     name, and keep the digests in `SHA256SUMS.txt` so a reader need not open a binary.
   - **RESOLVED:** adopted. `145-05`'s `files_modified` carries `runs/cycle1/run_0{1,2,3}.bin` and `145-06`'s
     carries `runs/cycle2/` and `runs/cycle3/`, with the digests in `SHA256SUMS.txt`.

5. **`--auto`/`--chain` vs `mode: YOLO` in `.planning/config.json`.**
   - Known: D-20 forbids auto-modes; `config.json` sets `"mode": "YOLO"` and
     `"_auto_chain_active": false`.
   - Recommendation: the planner sets `autonomous: false` on every plan **and** the dispatching
     command must be issued without `--auto`/`--chain` — the frontmatter alone is not self-protecting
     (D-20's own wording).
   - **RESOLVED:** adopted. All nine plans carry `autonomous: false`, and the dispatch mode is additionally
     recorded as a `Dispatch mode` row stubbed by `145-01` and filled from the operator's own words at
     `145-03` Task 1.

---

## Sources

### Primary (HIGH confidence — read or executed this session)

**Firmware, `/workspaces/firestarter` @ `a594173`:**
- `src/proms/eprom.cpp` — `eprom_internal_write_init_body:143-160` (erase gate), `eprom_internal_erase:588-604`, `eprom_check_vpp:525-586` (VPP band), the per-byte loop `:330-479`, the `#ifndef SERIAL_ON_IO` emission `:398-403`, `last_emit_ms:326-328`, `configure_eprom:40-110`
- `include/eprom.h:73-85` — `EPROM_PROGRESS_EMIT_INTERVAL_MS 1000` + its own frames-per-block rationale
- `src/eprom_operations.cpp:33-39` — the `FLAG_CAN_ERASE` op-layer gate that emits `MSG_ERR_NOT_SUPPORTED`
- `src/proms/eprom_params.cpp:22,46-52` — the 0x07/0x08/0x0B rows
- `src/proms/eprom_budget.cpp:42-118` — `eprom_block_budget_s` (the 8 s / 244 s figures)
- `src/firestarter.cpp:155-212` — the MSG_OK_READY CAP-01/02/03 pack block
- `src/proms/memory.cpp:490,541,557-467` — `BLANK_CHECK_CHUNK_SIZE 2048`, the INIT-phase emission
- `include/firestarter.h:54,156` — `FW_VERSION`, `FLAG_CAN_ERASE`
- `include/version.h` — `VERSION "3.0.0b17"` (and `git show origin/beta:` → `"3.0.0b18"`, `git show 3085084:` → `"3.0.0b17"`)
- `scripts/baseline/size_baseline.json` — leonardo 26906/28672/1766, RAM 2014
- `scripts/check_size_baseline.py:60-107` — the canonical `--policy merge05` invocation
- `tests/test_flash_path_record_sync.py:1247`, `tests/test_trace_segment_exhaustiveness_v131.py:1070,1184`, `tests/test_requirement_case_mapping_v131.py:753,802` — porcelain assertions
- `platformio.ini` — leonardo `DATA_BUFFER_SIZE=1024`, uno/uno328pb `SERIAL_ON_IO`

**Host, `/workspaces/firestarter_app` @ `68820a6`:**
- `firestarter/database.py:560-626` — `convert_to_programmer`'s `FLAG_CAN_ERASE` derivation
- `firestarter/eprom_operations.py` — `bar_format:68`, `DEFAULT_RUN_OUTPUT_DIR:76`, `WRITE_BLOCK_TIMEOUT_FALLBACK_S:126`, `ClassProgressHandler:369-410`, `_write_block_timeout:444-477`, `_apply_write_progress:702-751`, `_main_phase_send_data:753-889`, `consistency_check_eprom:978-1180`, `write_eprom:1862-1987`, `verify_eprom:1989-2023`, `build_flags:302-340`
- `firestarter/cli_handlers.py` — `read:515-543`, `write:546-800`, `erase:852-898`, `vpp/vpe:947-968`, `hw:976-982`, `config:985-1023`, `fw:1059-…`, group `-v/-p:405-442`, `dev read:1346-1374`, `dev consistency-check:1498-1585`, `_DEV_TOOLS_ENABLED:1291`
- `firestarter/serial_comm.py:395-441` (CAP-03 decode), `:672-697` (port list), `:815-906` (`_probe_port`, the `[\d.x]+` truncation), `:922-970` (`find_and_connect`)
- `firestarter/channel.py:144-173` — `is_dev_tools_enabled`
- `firestarter/firmware.py:141-190,190-209` — GitHub asset resolution; the version/controller report line
- `firestarter/hardware.py:207-320` — the voltage monitor loop
- `tools/gen_test_image.py` (all 79 lines), `tools/check_no_community_support_status_write.py` (header)
- `tests/test_py32_flash_map_host.py:391`, `tests/test_cap03_ack_layout_parity.py:746,786`, `tests/test_py32_asset_name_host.py:323` — sibling-porcelain assertions
- `tests/golden/chip_database_field_inventory.json` — the field-count golden recorded at `4d18b645`

**Executed this session (measurements, not readings):**
- `EpromDatabase().convert_to_programmer()` over 5 chips → the wire-flag table (RQ-1)
- `git merge-base HEAD origin/beta`, `git diff 4d18b645..HEAD -- …` → BENCH-03 (RQ-6)
- `pio run -e leonardo --target size` → 26906 / 2014
- tqdm non-TTY probe → frame shape, `refresh()` vs `update()` behaviour (RQ-4)
- address-stamped image generator → SHAs, 0xFF counts, 0→1 transition percentages, A8-fault decode (RQ-2)
- `pytest` with and without a planted untracked file in `/workspaces/firestarter` → **9 RED** (RQ-9)
- `firestarter info W27C512`, `firestarter dev consistency-check --help`
- `serial.tools.list_ports.comports()` → no ACM device attached
- `pio --version`, `avrdude -v`, `which script stdbuf ts`

### Secondary (HIGH — project record, cross-checked against code)

- `.planning/phases/145-bench-validation/145-CONTEXT.md` — D-01…D-20 (the binding contract)
- `.planning/REQUIREMENTS.md:245-252` — BENCH-01…03 verbatim
- `.planning/STATE.md:113-124` — standing bench restrictions
- `.planning/phases/99-.../99-03-BENCH-LOG.md` — the record template + the `0x08` prior state
- `.planning/phases/79-25v-nmos-ceiling-raise/79-01-SUMMARY.md`, `79-02-SUMMARY.md` — the `0x0B` prior state
- `.planning/phases/143-.../143-HOST-RECORD.md` §4, §5 (items 1, 3, 5, 6, 7), §10 H4 — the 4687 µs threshold, the `leonardo`-only non-claim, the A1 `[ASSUMED]` figure
- `.planning/phases/144-.../144-TEST-RECORD.md` §10 H6/H7
- `.planning/debug/resolved/write-empty-input-regression.md` — **the 22.84 s 64 KiB W27C512 Leonardo write and the "two distinct progress bars" observation**
- `.planning/todos/completed/w27c512-eeprom-misclassification.md` — the erase-history chain
- `.planning/MILESTONES.md:301, 353-357, 406, 444` — Phase 77/90/91/92 and Phase 79 outcomes
- `firestarter_app/CLAUDE.md`, `firestarter/CLAUDE.md`, `/workspaces/CLAUDE.md`

### Tertiary (LOW — none load-bearing)

No web search was performed. Every claim in this document is sourced from the working tree, the
project record, or a command executed this session. Two timing predictions (A1, A2) are explicitly
marked `[ASSUMED]` and carry named mitigations.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| D-03 erase capability (RQ-1) | **HIGH** | Wire flags computed by executing the shipped host code; firmware call site read; three prior bench records corroborate; the contradicting record is dated pre-fix |
| D-05 image recipe (RQ-2) | **HIGH** | Generator written and executed; all properties measured, including the simulated address-line-fault decode |
| CLI command surface (RQ-3) | **HIGH** | Every option read from source; `--help` executed against the installed CLI |
| D-10 mechanism (RQ-4) | **HIGH** | Emission site, guard, cadence constant and per-block locality all read directly; capture behaviour probed empirically |
| D-10 timing prediction (RQ-4) | **MEDIUM** | Derived from a recorded 22.84 s pre-v1.31 write + an in-tree estimate; the v1.31 loop was not timed. Mitigation is built into the recommendation (Gate 3) |
| D-18 reflash route (RQ-5) | **HIGH** | `firmware.py`'s GitHub resolution read; `VERSION` compared across three refs; the 26906 B figure measured |
| avrdude log wording (RQ-5) | **MEDIUM** | avrdude 8.1 confirmed installed; its exact upload wording could not be observed without a board |
| BENCH-03 (RQ-6) | **HIGH** | All four legs executed; merge-base confirmed rather than assumed |
| VPP band (RQ-7) | **HIGH** | Both comparisons read from `eprom_check_vpp`; arithmetic trivial |
| Record shape + prior numbers (RQ-8) | **HIGH** | Read verbatim from the two source records |
| Suite tripwires (RQ-9) | **HIGH** | Proven by planting and removing a probe file; 9 failures observed by name |
| Environment availability | **HIGH** | Every tool probed |

**Research date:** 2026-08-15
**Valid until:** ~2026-09-14 for the code-derived facts (stable branch, no source change permitted
in this phase). The two `[ASSUMED]` timing figures are superseded the moment cycle 1 runs.
