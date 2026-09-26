# Phase 151 Plan 14 — Bench Session Record

**Session date:** 2026-08-20
**Operator resolution basis:** Task 1's checkpoint was pre-resolved by the operator's verbatim
reply — *"W29C020 is seated in the Leonardo, shield 2.0, no W29C040 is available"* — before this
session began driving any port. Task 3's checkpoint was pre-resolved the same way: no `W29C040`
sample exists on the bench, so leg C did not run.

This record follows `151-VALIDATION.md`'s Unsatisfiable-Criteria list and `151-DESIGN.md` §8's
evidence ceiling throughout. Nothing below claims either sequence is correct or validated.

---

## Session identity

- **Board:** Leonardo (ATmega32U4).
- **Device path:** `/dev/ttyACM0`, confirmed this session (not carried over from a prior one).
  `/dev/ttyACM1` is the `uno` and was not touched; `/dev/ttyUSB0` runs pre-CAP-02 firmware and was
  not touched.
- **`controller:` identity, read this session:** `leonardo on port /dev/ttyACM0`, from
  `firestarter -p /dev/ttyACM0 fw`'s own output: *"Current firmware version: 3.0.0b19, for
  controller: leonardo on port /dev/ttyACM0"* — read identically before and after the sideload
  below (the version string does not change; see the discriminator note).
- **Shield revision:** **Rev 2.0**, as stated by the operator. This is **operator-stated, not
  probeable** — the EEPROM `hw_revision` field cannot distinguish Rev 2.2 from Rev 2.0 from the
  modified Rev 0. `firestarter -p /dev/ttyACM0 hw` reported *"Hardware revision: Rev 2.0-class,
  Override HW: Rev 2.0-class"*, which is **consistent with**, but is not independent proof of,
  the operator's Rev 2.0 statement.
- **Part seated: `W29C020`**, marking as stated by the operator. The operator did not distinguish
  a suffix, and per the C-17/C-18 finding (`151-DESIGN.md` §5) it does not matter: `W29C020`,
  `W29C020C` and `W29C022` are one upstream `<ic>` entry sharing one `chip_id 0x0000da45`, so the
  three are **indistinguishable on the wire** — firmware cannot tell which of the three is in the
  socket regardless of which suffix the operator read off the package. Recorded as operator-stated
  with the suffix **not distinguished**, per orchestrator constraint 4.
- **Part not seated / not on the bench: `W29C040`.** No sample is available. Leg C did not run;
  see §Leg C below.
- **Firmware flashed:** the Phase 151 firmware build, `firestarter` submodule HEAD
  `373d6da7d674883f09b0a2e582851461f0e6c561` — *"test(151-10): sever eight reddened legs onto a new
  `*_v151*` fixture family"* — the tip of the tree at the time this plan ran, which includes
  `CMD_LOCK_STATUS` (landed at `0444b1c`, plan `151-08`). Sideloaded via
  `pio run -t upload -e leonardo --upload-port /dev/ttyACM0` from `/workspaces/firestarter`
  (**not** `fw --install`, which installs a published release and ignores `--board`). Firmware
  build provenance is recorded here explicitly so this run is attributable — the defect Phase 147
  existed to remove (`fw_board_identity` previously read `null` on every report before Phase 147).
- **Host CLI:** the py3.11 venv at
  `/tmp/claude-1000/-workspaces/f3ebf666-a01b-4de4-9860-8a006054ba0c/scratchpad/p151/venv311`,
  reporting `Firestarter, version 3.0.0b21`; `firestarter_app` submodule HEAD
  `4a6f5e8d52a53097fcafb8e95efce8ff42f82a48`.

### Flash-size check, performed before uploading

```
$ pio run -e leonardo
...
RAM:   [========  ]  78.8% (used 2016 bytes from 2560 bytes)
Flash: [========  ]  83.9% (used 27500 bytes from 32768 bytes)
========================= [SUCCESS] Took 0.42 seconds =========================
```

**27500 B** against the **28672 B** Caterina cliff — **1172 B** of margin, matching the orchestrator's
funded expectation exactly. The upload was **not** aborted (it did not need to be); this is the
re-measurement the orchestrator's constraint 1 required before uploading.

### Sideload transcript

```
$ pio run -t upload -e leonardo --upload-port /dev/ttyACM0
...
Configuring upload protocol...
AVAILABLE: avr109
CURRENT: upload_protocol = avr109
Looking for upload port...
Using manually specified: /dev/ttyACM0
Forcing reset using 1200bps open/close on port /dev/ttyACM0
Waiting for the new upload port...
Uploading .pio/build/leonardo/firestarter_leonardo.hex

avrdude: AVR device initialized and ready to accept instructions
avrdude: Device signature = 0x1e9587 (probably m32u4)
avrdude: writing flash (27500 bytes):
avrdude: 27500 bytes of flash written
avrdude: verifying ...
avrdude: 27500 bytes of flash verified

avrdude done.  Thank you.
========================= [SUCCESS] Took 6.16 seconds =========================
```

The Leonardo reset into its bootloader on a transient port during the upload (normal `avr109`
behavior) and re-enumerated as `/dev/ttyACM0` afterward — confirmed with `ls /dev/ttyACM*`.

### Verifying the flash actually took (the discriminator, not the version string)

`firestarter -p /dev/ttyACM0 fw` reported the **identical** string both before and after the
sideload: *"Current firmware version: 3.0.0b19, for controller: leonardo on port /dev/ttyACM0"*.
This is **weak evidence only** — the host's `[\d.x]+` version probe truncates the pre-release
suffix and cannot distinguish the beta with `CMD_LOCK_STATUS` from the beta without it.

The **strong discriminator**, as specified by orchestrator constraint 1, is `dev lock-status`'s
own behavior on unknown-command firmware:

**Before the sideload** (firmware `3.0.0b19`, pre-`151-08`), `dev lock-status W29C020 --force`:

```
Connecting...Connecting... OK
Reading protection status for W29C020
ERROR: Unknown command: 16
Programmer error during LOCK_STATUS: Programmer error during init: Unknown command: 16
Protection status read for W29C020 did not return OK. Programmer response: Programmer error during init: Unknown command: 16
unadjudicated_probe --force ran the read past the table's 'undocumented_alias' refusal; the result is an unadjudicated probe, never a state claim (D-07).
```
Exit code: `4`.

**After the sideload**, the identical command:

```
Connecting...Connecting... OK
Reading protection status for W29C020
Protection status read for W29C020: (main done)
unadjudicated_probe --force ran the read past the table's 'undocumented_alias' refusal; the result is an unadjudicated probe, never a state claim (D-07). (raw byte: 0xFE)
```
Exit code: `4`.

**The "Unknown command: 16" comms error is gone, and a real raw byte (`0xFE`) is returned instead.**
That is the confirmation the flash took — `CMD_LOCK_STATUS = 16` now exists on this board. Both the
before and after runs happen to render under the same `unadjudicated_probe` class token and the
same exit code `4`, because `--force` labels *any* outcome of the forced read path (success or
comms failure alike) as an unadjudicated probe — the class token itself is not the discriminator
here; the presence or absence of the `Unknown command: 16` text, and of a raw byte, is.

---

## Leg A — mode entry and exit

**Run:** `firestarter -p /dev/ttyACM0 id W29C020` (verbose, `-v`, to expose the expected chip-ID
value the firmware compares against).

```
$ firestarter -v -p /dev/ttyACM0 id W29C020
...
DEBUG  :EpromOperator: 508: EPROM data: {..., 'chip-id': 55877, ...}
...
INFO   :EpromOperator:2216: Chip ID check passed for W29C020: (main done) (0.03s)
```
Exit code: `0`.

`55877` decimal is `0xDA45` hex — the DB's expected chip ID for the `W29C020,W29C020C,W29C022`
entry. `CHECK_CHIP_ID` on this firmware only reports "passed" when the value it reads back from
silicon matches the value it was told to expect; a mismatch is reported as a failure (or, with
`--force`, a downgraded warning), never silently as "passed". "Chip ID check passed" with exit `0`
is therefore the verbatim confirmation that the read-back value was `0xDA45`.

**One attempt was sufficient** — no timeout occurred, so no retry was needed. (This board is the
Leonardo, not the bench-unstable `uno328pb` on Rev 2.2 the retry guidance names; a clean pass on
the first attempt is recorded as such, not padded with an unneeded retry.)

**What this sub-claim earns, in these words and no more: it confirms sub-claim (i), Product-ID mode
entry and exit, on this exact part and socket.** A correct chip-ID read is a positive control on
the `AA/55/90` → read → `AA/55/F0` transition. **It earns nothing about the status address, the
decode, or the chip's actual lock state** — those are sub-claims (ii), (iii) and (iv), and none of
them has an oracle (see §Leg B).

Since `0xDA45` was confirmed, leg B was run (see below).

---

## Leg B — the `0x05` probe on the `W29C020`

### Unforced run

```
$ firestarter -p /dev/ttyACM0 dev lock-status W29C020
undocumented_alias W29C020: not documented in lockable-proms.md: W29C020 (documented-not-readable) [lockable-proms.md:21 names the row key 'W29C020 / W29C020C' (Yes-special, covering both parts), but every restatement elsewhere in the document -- lockable-proms.md:30, :335, and :350 -- names 'W29C020C' only, never bare W29C020. Bare W29C020 appears exactly once in the document's 399 lines: the :21 row key itself. Tiebreak rule (DESIGN.md §5): the more-restrictive reading wins, so W29C020 curates to documented-not-readable.]; W29C022 (undocumented)
```
Class token: `undocumented_alias`. Exit code: `2`.

This is the live demonstration of D-06's accepted consequence: `W29C022` is named as
`(undocumented)`, exactly as the plan anticipated, and no `0x05` row answers by default — not even
the operator's own, physically-seated `W29C020`.

### Forced run

```
$ firestarter -p /dev/ttyACM0 dev lock-status W29C020 --force
Connecting...Connecting... OK
Reading protection status for W29C020
Protection status read for W29C020: (main done)
unadjudicated_probe --force ran the read past the table's 'undocumented_alias' refusal; the result is an unadjudicated probe, never a state claim (D-07). (raw byte: 0xFE)
```
Class token: `unadjudicated_probe`. Exit code: `4`. **Raw status byte: `0xFE`.**

Recorded as observed, either way, with no validation claim attached: `0xFE` happens to match
`151-SEQUENCES.md`'s decode table's "boot block locked" value (`0xFE`; `0xFF` would read
"not locked"). **Stating that match is not a validation** — sub-claims (ii) the status address and
(iii) the decode have no oracle (see the table below), so a byte that looks plausible is a
plausibility observation, not a verification of either the address or the decode being correct.

### The four sub-claims, decomposed

| Sub-claim | Established this session? | Reason |
|---|---|---|
| (i) Product-ID mode entry and exit work on this part/socket | **Yes** — leg A, `0xDA45` | Positive control on `AA/55/90` → read → `AA/55/F0` |
| (ii) the status address (`0x0002`) is right | **No** | No ground truth exists for what is actually at that address; the address is analogy-derived (see below), not datasheet-page-confirmed |
| (iii) the `0xFF`/`0xFE` decode is right | **No** | Would require independently knowing the part's true lock state, which this session has no way to obtain |
| (iv) the boot block **is** locked | **No, not without self-contradiction** | The only independent oracle is write→verify — destructive, and the *indirect* method `lockable-proms.md:3` explicitly excludes from the definition of "readable" |

No write, erase or verify operation was run on this part in this session.

### The provenance this leg's read address and decode actually rest on

Per `151-SEQUENCES.md`, Sequence B's status-read address (`0x0002`) and its `0xFF`/`0xFE` decode
are the artifact's **lowest-confidence citation** — sourced by structural analogy to the
already-working manufacturer/device word pair (`0x0000`/`0x0001`), not independently re-checked
against a locally-held datasheet page (no `W29C0xx` datasheet exists anywhere in this container).
The operator chose `web-sourced-with-citation` at plan `151-04`'s checkpoint. Per OD-4, the pinned
bytes this sequence relies on are **a change detector, never a correctness proof** — this session's
raw byte, whatever it is, is data about what this specific chip returned at that address under
this analogy-derived sequence, not proof that the sequence itself is right.

---

## Leg C — the `0x05` probe on the `W29C040`

**Not run.** The operator's stated reason: *"no W29C040 sample available on the bench"* (operator,
2026-08-20). Task 3's checkpoint was pre-resolved with this reply before this session began, and
per this plan's own instruction ("If the operator said `skip bench` or `skip leg C`, write the
artifact anyway with the skipped legs recorded as not run, with the stated reason"), no command
was run against the physically-seated `W29C020` under the `W29C040` name — doing so would have
produced a reading from the wrong physical part and misattributed it to `W29C040`.

Neither the unforced refusal nor the forced probe was executed. For completeness (not as a
substitute for a live run): the `W29C040,W29C042` DB entry's unforced refusal is known, from
`151-DESIGN.md` §5 and the CLI's own code path, to refuse for **two independent reasons in
different states** — `W29C040` is `Variant-dependent` per `lockable-proms.md:22` (not a clean
`documented-readable`), and `W29C042` is undocumented, matching neither entry name in
`lockable-proms.md` at all — but this session did **not** observe that refusal live, and the record
must not claim it did.

**D-03's cap, restated verbatim for this leg specifically, even though the leg did not run this
session:** no artifact may claim the `0x05` sequence is silicon-validated on the strength of a
`W29C040` leg, run or unrun. That cap is unaffected by leg C's absence this session — it was never
satisfiable by this leg to begin with, only bounded by it.

**Consequence for the v1.17 RCA:** see §What this session did not establish below. Leg C's absence
this session makes the RCA's non-closure final for this phase — Phase 151 has no further bench
plan after `151-14`.

---

## Leg D — the `0x06` Autoselect read

**No bench leg exists** for the `0x06` Autoselect sector-protect-verify sequence, anywhere in this
phase's plans. It was **not run** — there is no part on this bench that exercises the `0x06`
handler under `dev lock-status`, and none was sought, because no such leg was ever planned.
`lock-status` on a `0x06` part therefore ships **software-proven and unrun on silicon**.

---

## What this session did not establish

- **That either sequence is correct, or validated.** Both the `0x06` Autoselect sequence and the
  `0x05` Winbond boot-block sequence are datasheet-derived: `infoic.xml`'s `config` field is the
  literal string `"NULL"` on all 101 `protocol_id="0x05"` entries and all 897
  `protocol_id="0x06"` entries, so neither has a machine-readable oracle. The strongest available
  test over either is a pinned literal byte table plus a citation comment — a
  **change detector, not a correctness proof.** Leg A's `0xDA45` result and leg B's `0xFE` raw byte
  are both real, recorded observations; neither is evidence that the sequence producing them is
  correct.
- **Anything about `W29C020C` or `W29C022` specifically.** All three `W29C020*` aliases —
  `W29C020`, `W29C020C`, `W29C022` — are one upstream `<ic>` entry with one chip id
  `0x0000da45`, so they are **indistinguishable on the wire**: the firmware cannot tell which of
  the three is in the socket, and this session's reads say nothing that separates one alias's
  behavior from another's. This is the measured reason a family-level claim from this one part is
  *less* supportable than it might look, not more — and it is exactly why D-06's one-entry-one-answer
  rule (refusing the whole `W29C020,W29C020C,W29C022` entry unless every alias is documented) is
  right here, independent of how the operator's package marking read.
- **Closure of the v1.17 `W29C040` locked-boot-block RCA.** That RCA asked for a second `W29C040`
  sample. This session had none — leg C did not run (see §Leg C) — so the payoff that funded
  Sequence B in the first place (closing that RCA from the read side) is **not delivered**, even
  partially, this session. A `W29C020` read, had one been comparable, would at most have been
  partial corroboration from the read side on a *different* part; with leg C entirely unrun there
  is not even that much to report for the RCA specifically. **The RCA remains open.**
- **Anything about AT28C or protocol `0x0D` silicon.** The milestone's Evidence Ceiling is
  unchanged by this session: `0x0D` stays `UNVERIFIED`, no `support_status` field changed, no
  AT28C part exists in inventory, and gh#21, gh#32, gh#11 and gh#12 all stay open. This phase adds
  no `0x0D` read path at all.
- **No requirement was flipped, and no claim was upgraded, by this plan.** LOCK-02 and LOCK-03
  were already `Complete` before this session, flipped by `151-13` on host and firmware-native
  software evidence. This bench session adds bench observations to the record; it does not touch
  `REQUIREMENTS.md`, and nothing observed here justifies touching it.

---

*Phase: 151-protection-readability-lock-status*
*Plan: 151-14 (bench session)*
*Recorded: 2026-08-20*
