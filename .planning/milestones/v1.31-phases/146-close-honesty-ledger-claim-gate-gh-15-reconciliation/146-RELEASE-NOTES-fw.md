# Firmware prerelease — 27C EPROM per-byte pulse-to-verify loop

**Version:** `3.0.0b19` — read from `gh release list --repo henols/firestarter` at 2026-08-18T10:00:08Z, never predicted. Cut by `beta-build.yml` from merge commit `bc3ca547` (PR #52). Assets published: `firestarter_leonardo.hex` (75961 B), `firestarter_uno.hex` (70120 B), `firestarter_uno328pb.hex` (70246 B), `firestarter_py32f071.hex` (79047 B). The host app's matching release is **`3.0.0b21`** — the two repositories version independently, so the numbers do not agree and are not expected to.

This is a prerelease build of the firmware for the RURP shield. It carries the three AVR board
builds as attached assets — `firestarter_leonardo.hex`, `firestarter_uno.hex`,
`firestarter_uno328pb.hex` — plus `firestarter_py32f071.hex` if the ARM build lands on this
release's own listing at cut time. The normal way to install one is `firestarter fw --install`,
which pulls the file matching your host app's release channel and your `--board` choice; every
file is also attached directly to this release if you need to flash by hand.

## The headline: 27C programming now runs a per-byte pulse-to-verify loop

The three 27C UV/EE-EPROM protocols — `0x07`, `0x08` and `0x0B` — now program with a per-byte
pulse-to-verify loop: a fixed-width pulse, read from the chip database for every byte rather than
baked in as a protocol constant, is applied and the byte is re-read; on a mismatch the same pulse
repeats, never growing wider, until it converges or a per-protocol backstop is exhausted. A byte
that exhausts its backstop now fails by reporting its own address and pulse count, rather than
failing the block opaquely.

State the boundaries here, immediately, because they are the whole shape of what shipped:

Bench evidence exists for exactly one of these three protocols, on one part, one controller and
one shield revision — the Winbond **W27C512** (chip id `0xda08`) on a **`leonardo`**-class
controller, shield Rev 2.0. The other two protocols are **skipped-with-reason**: `0x08` needs an
AM27C020 and `0x0B` needs an M2716 or M2732, neither of which was on the bench this milestone.
Neither disposition is inferred from the `0x07` result.

Intra-block write progress — seeing a long write's position update while it runs, instead of it
appearing to hang — reaches the `leonardo` controller class only. On `uno`/`uno328pb`-class
controllers the emission is compiled out **structurally**, not by choice: those boards tear the
UART down for the whole programmer-mode window, and a buffered progress frame there could silently
displace a later error frame, turning a program failure into a transport timeout instead of a
reported one.

And the ARM `py32f071` build target: it was compiled once, locally, against this milestone's code
for the first time this phase, emitting exactly one image under the firmware repository's own
build oracle. That is a **delta** against a target no CI run has ever compiled against any of this
milestone's code — it is **not** CI parity, because the local toolchain resolved four bare-metal
library packages the CI install does not name by itself, and no PY32F071 circuit board exists
anywhere in this project. Neither repository's CI has run against any of this milestone's code.

## New capability: a per-run pulse override

The host can override the per-run pulse width for a single write via `firestarter write --pulse-us
N` (1–65535 microseconds), riding the existing wire field rather than adding a new one. That bound
is parity with another programmer's own integer pulse-width field — it is **not** a wire-type or
hardware limit.

On the firmware side, the only pre-flight refusal keyed to this value is a per-protocol energy
cap: non-zero on `0x0B` (an over-cap value there is refused before any high voltage is enabled) and
zero — uncapped — on `0x07` and `0x08`. On those two rows there is no firmware-side upper bound
today. Backlog **999.31** owns the decision of whether to add one; nothing here should be read as
a fix for that gap.

## Before you plug anything in

Skipping the pre-write erase (`--skip-erase`) leaves un-erased bits on a non-blank
electrically-erasable chip that cannot be reprogrammed afterward — use it only on a chip that is
already blank or that cannot be erased at all. `--force` overrides a VPP or chip-id mismatch and
should be treated as a deliberate override, never a default choice.

The hardware fact that matters most: the raised program-VCC the vendor algorithms assume for
threshold margin — around **6.25 V** above nominal — is unreachable on this shield, which has no
VCC-raise path. This release buys timing, pulse-count and verify fidelity, and **not**
silicon-margin fidelity.

## What is established

- A single `protocol_id`-keyed table carries each 27C protocol's shape — max pulses, overprogram
  factor and cap, verify mode, VPP path — while the pulse width itself stays a chip-database
  datum, never a protocol constant.
- The per-byte loop as shipped: fixed-width pulses, verified after each one, no width growth
  between attempts; a byte already matching, or already blank, is skipped without a pulse.
- A byte that fails to verify within its protocol's pulse backstop aborts the block, disables
  every active high-voltage route, and reports the failing address and pulse count.
- One routing-mask function now drives both the pre-write voltage check and every write and error
  exit; every exit path — success, verify failure, budget failure, error return — disables every
  active route.
- All three AVR targets build and pass, carrying a named, commit-attributed +96 B flash-band
  exemption over the prior milestone's band on every target — admitted as a defect fix restoring
  behaviour the pre-v1.31 firmware already had, stated plainly rather than folded into a moved
  band anchor, and not remediated.

## What this release does not establish

- **No comparative claim.** This release is not faster or more reliable than what preceded it —
  no control run was made, and a historical pre-milestone write-time figure that exists elsewhere
  in this project's records is a recorded number, not a control measurement.
- **No claim, in either direction, about how closely this matches any datasheet's own timing.**
  That question is out of scope for every record this milestone kept, cited but not quoted here
  because its own source wording collides with this project's release-note vocabulary.
- **`0x08` and `0x0B` remain unvalidated on real silicon.** Both are implemented and exercised
  off-hardware only; neither has run a single byte on a physical part this milestone.
- **The root cause of an intermittent single-byte margin failure remains open.** It is mitigated
  by a settle-time increase and has held clean across roughly a dozen and a half cycles since —
  that is not the same as a root cause, and none has been found.
- **The program-window supply rail's behaviour under load has never been instrumented.** The only
  available proxy instrument is defeated by a standing tooling gap, so nothing in this milestone
  says anything about what that rail actually does while a write is running.

## The capability boundary, and what would help

Today's 27C position is: one protocol validated end to end on one part, a per-run pulse override
that reaches the wire, and two protocols with a real but unexercised implementation. It is not: a
claim about either of the other two protocols on real silicon, or a claim about matching a
datasheet's timing more or less closely than any earlier release.

If you have an AM27C020 or an M2716/M2732 on hand, running a write with this release and reporting
back — either outcome — is the single most useful thing you could send for either protocol. A true
ultraviolet-erase `0x07` data point (a TMS27C512) would also help, even though the algorithm under
test is identical to the part already validated.
