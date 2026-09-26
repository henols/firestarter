# Firmware prerelease — the PY32F071 target publishes as a real release asset

This is a beta build of the firmware for the RURP shield. It carries four board builds as
attached assets for the first time: `firestarter_leonardo.hex`, `firestarter_uno.hex`,
`firestarter_uno328pb.hex`, and — new in this release — `firestarter_py32f071.hex`. The normal
way to install one is `firestarter fw --install`, which pulls the file matching your host app's
release channel and your `--board` choice; all four files are also attached directly to this
release if you need to install by hand.

## The headline: a PY32F071 image is now a published release asset

The PY32F071 build target builds clean and links a complete image inside CI, in the same job that
has always produced the three AVR files. For the first time, that image — `firestarter_py32f071.hex`
— is attached to this release exactly the way the AVR files always have been. The host app's
`fw --board py32f071` install path, which shipped in an earlier beta with nothing to point at, now
has a real file to resolve.

State the boundary immediately, because it is the whole point of this section: **no PY32F071
circuit board exists anywhere in this project**, on a bench or otherwise, and no PY32F071 chip has
ever received this image. Publishing the file is the entire event described above — nothing here
is a claim about that file running on anything.

## New capability: a py32 board choice, gated to beta by construction

Alongside the image, the host app gained a pure-Python DFU installer for it
(`firestarter/py32_dfu.py`), plus `fw --dfu-probe` and `--usb-id` for identifying which USB device
to talk to when more than one is attached. All three are driven by `_BOARD_CHOICES`, a list
computed from your installed app's version the moment its CLI module is imported — so a stable
release of the host app hides `py32f071` entirely: `fw --help` on a stable install lists only the
three AVR boards, and both `--dfu-probe` and `--usb-id` are rejected outright. There is no
environment variable that turns any of this on early. If your host app is on a pre-release
channel, you can point the installer at this file today; on a stable channel, there is
deliberately nothing new to see yet.

## The USB identity this image presents

The descriptor `firestarter_py32f071.hex` presents now reads pid.codes' `1209:0001`, replacing a
pair that was, until this release, copied verbatim from the silicon vendor's own SDK example — a
vendor identity this project was never entitled to present as its own. `1209:0001` is pid.codes'
own documented **private-testing** product id, reserved for exactly this kind of in-house use; it
is **not** an allocated PID. The source carries a comment saying so, worded the way pid.codes' own
terms ask (not require) — that source referencing this pair should warn a reader that the id is
not universally unique.

This project's own ship gate is unchanged by this release: no PY32F071 board ships, and no release
advertises a USB identity, until a PID allocated under vendor id `0x1209` exists. This release does
not close that gate — an allocation request is a separate, tracked, human-filed step that has not
happened yet — and makes no claim that it does. Whether disclosing a caveated, explicitly
non-allocated test id in a published image counts as "advertising a USB identity" is a judgment
call this project records rather than resolves here; a future reader may reasonably decide
differently.

## Before you plug anything in: the socket must be empty

Before any PY32F071 firmware install — DFU, SWD, or otherwise — the PROM socket must be empty.
This instruction is stronger here than the equivalent warning on the AVR boards, because the
PY32F071 pin map is provisional **by declaration, not by omission**: every signal assignment
except the VPP-sense channel is a placeholder chosen only to keep a simple, contiguous data bus,
and none of it has ever been checked against a real board. A provisional map can get a signal's
*direction* wrong, not just its identity — and a wrong-direction pin on a socket holding a chip can
destroy that chip silently on first power-up. A DFU install makes this worse, not better: the
board re-enumerates with its boot strap held high, in a mode where none of the application's own
startup pin levels are in effect — whatever the factory bootloader leaves the pins doing is what a
seated chip sees.

## What is proven, stated exactly

- The PY32F071 target builds clean and links a complete image inside CI, in the same job as the
  three AVR images (CI run `30722352902`, 22 of 22 steps succeeded).
- The published image's version string matches the version CI embeds, read from that same run's
  own step summary.
- A deliberately broken ARM build was rehearsed against this pipeline to confirm it cannot take
  the AVR release down with it: the three AVR files still published, with a warning annotation
  naming the missing py32 asset (a second CI run, `30722537152`, using a planted fault, not an
  observed regression).
- Leonardo flash does not grow (26072 → 26016 bytes, a 56-byte reduction); Uno-class flash growth
  is small and recorded (Uno +22 bytes, uno328pb +28 bytes); RAM is unchanged on every AVR target.
  None of this is about the PY32F071 target — it is recorded here because this release shares one
  merge with those numbers.
- The native register-trace suite (`pio test -e native` and `-e native_nodevtools`) still passes
  at its long-standing count, 141 test cases across 17 suites, unchanged by anything in this
  release. This suite runs the AVR-family emulation host; it does not exercise anything compiled
  for the ARM target.
- The host app's own test suite passes in full at its currently recorded total, 1303 tests.
- The DFU install sequence — device discovery, the DfuSe-versus-plain-DFU dialect fork, and the
  readback-and-verify step — is exercised against synthetic USB device descriptors and a mock USB
  transport, never against a real device.
- The DFU protocol's opcode literals are anchored against the published USB DFU 1.1
  specification, fetched and read independently of the code under test.

## What is NOT proven

**No PY32F071 hardware exists.** Nothing in this milestone has ever run on this silicon, and
nothing in it can — there is no PY32F071 circuit board anywhere in this project, so nothing above
is a claim about a board; every item above is a claim about a file, a build, or a test suite.

Four specific gaps, named because a release note that lists only wins reads as more finished than
it is:

- **The pin map is a placeholder with no schematic to check it against**, and nothing in this
  release changes that.
- **There is no bus-trace oracle on the ARM target.** The register-write recording harness this
  project uses to catch a wrong emitted sequence runs only on the native (AVR-emulation) host; the
  ARM target's own emitted sequences have never been captured or compared against anything, so a
  divergence there would currently go unnoticed by anyone.
- **USB-interrupt-versus-PROM-pulse timing is unmeasured on this target.** The write path spins
  with interrupts masked while a delay primitive busy-polls a timer; whether that holds inside the
  PROM's pulse-width budget on this silicon is unmeasured here — a different board's measurement
  exists elsewhere in this project's history and does not transfer to this one.
- **The DFU readback is checked against a mock only.** Every outcome of the readback-and-verify
  sequence — a match, a mismatch, a device that declines to support it — has been exercised
  against a mock USB device that answers exactly as it is told, never against a real bootloader.

None of the above says anything about whether this board, once one exists, would work as a
programmer. A firmware install completing — bytes transferred, and where a readback exists,
matched — says nothing about the assembled device driving a PROM's control signals. Those are two
separate claims, and this project keeps them separate everywhere, including here.

## The capability boundary

py32f071 support today is: a build target that builds clean, a release asset that gets published,
and a host-side installer that can attempt to write it to a device presenting the right USB
interface. It is not: a board anyone has powered on, a confirmed pin map, or a measured programmer
of any kind. Those next steps stay out of reach regardless of how many more times this pipeline
runs green, until a physical board exists.

## Feedback wanted

If you build a PY32F071 board and attempt an install with this release, please report back — good
or bad, that would be this target's first hardware data point of any kind. This section does not
address, and should not be read as addressing, any other open report on this project's tracker.
