# Host app prerelease — a PY32F071 firmware install path

`pip install --pre --upgrade firestarter`

This GitHub release carries no attached files — it is a tag-and-marker page only. PyPI is the
distribution channel for the host app; the command above pulls it. The matching firmware for this
release is published separately, and its `.hex` files — including, for the first time,
`firestarter_py32f071.hex` — are what `firestarter fw --install` pulls when you update your board.

## What the app gained: a PY32F071 install path with no external tool

`firestarter fw --board py32f071 --install` (or `--dfu-probe` to identify the device first) drives
a DFU 1.1 / DfuSe client this project wrote itself (`firestarter/py32_dfu.py`) over `pyusb` — no
`dfu-util` binary, no separate download. A board that isn't recognized still falls back to the
long-standing avrdude path, and every existing AVR asset name is unchanged. `--usb-id` lets you
point the installer at one specific USB device when more than one DFU-capable device is attached —
this devcontainer's own webcam is exactly the kind of unrelated device that option exists to rule
out, and the installer never touches a DFU runtime interface unless you name one this way. The new
dependency is opt-in: install `firestarter[py32]` (which pins `pyusb>=1.3.1`) to get it. The
installer finds a DFU-capable device by its USB interface class, not by vendor or product id,
because the identity the factory bootloader itself presents has never been independently
confirmed.

A previously-existing installer behavior is also tightened here, and it applies to every board,
not only this new one: if you name a board explicitly with `--board` and the programmer actually
attached disagrees, the install is now refused instead of silently proceeding with whichever board
was detected.

## The beta-only gate, by design

`_BOARD_CHOICES` — the list `fw --help` renders and validates `--board` against — is computed from
your installed app's version the moment the CLI module is imported. On a stable release, that list
holds only the three AVR boards, and both `--dfu-probe` and `--usb-id` are rejected outright at the
option parser. `firmware.py`'s own install path repeats the refusal one layer down, so a library
caller who imports the flashing code directly and bypasses the command-line parser entirely is
refused too, not only an invocation typed at a shell. There is no environment variable that turns
any of this on early, and a version string that fails to parse is treated the same as a stable one
— closed, not open. Widening this to a stable release is a one-line change (deleting one entry
from a list) once a board exists to justify it; nothing about that decision is made by this
release.

## What is proven

The host test suite passes in full at its currently recorded total, 1303 tests. A CI leg installs
the `py32` extra and exercises the real `pyusb` import and its actual API surface —
`usb.core.find`, `ctrl_transfer` — rather than a mock of the library itself. The DFU install
sequence, including the dialect fork between DfuSe-style and plain-DFU-1.1 readback, is exercised
against synthetic USB device descriptors and a mock transport across the host test suite.

## What is NOT proven

**No PY32F071 hardware exists.** Nothing in this milestone has ever run on this silicon, and
nothing in it can. The readback-and-verify step that confirms a write landed correctly has been
checked against a mock device only — every outcome (a match, a byte-level mismatch, a device that
cannot support readback at all) is a mock answering exactly as it is told, never a real
bootloader. The DFU dialect fork itself, the flash sector and erase geometry, the flash-envelope
bounds the installer refuses to write past, and the plain-DFU load address are all inherited from
published documentation and the linker script, not observed on a device. Puya's own DfuSe
application note (UM1504) — the one document that could independently confirm the vendor-specific
half of this protocol — could not be reached over the network during this milestone and remains an
open, network-unreachable residual. A successful install here means only that bytes were
transferred and, where a readback exists, that it matched — it says nothing about the assembled
programmer working.

Separately, and not a claim of this release: a pre-existing type-checking debt failure exists in
this project's primary CI job. It predates this release, this release adds nothing to it, and it
is not evidence about anything named above.

## Feedback wanted

If you build a PY32F071 board and try the install path above, please report back — good or bad,
that would be this target's first hardware data point of any kind. This section does not address,
and should not be read as addressing, any other open report on this project's tracker.
