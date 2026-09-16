---
id: avrdude-mcu-detection-fallback
title: avrdude MCU-detection fallback for blank-chip / wrong-firmware recovery
captured: 2026-05-21
status: pending
type: enhancement
target_milestone: v1.6+
priority: low
related_phase: 23
resolves_phase: null
---

# avrdude MCU-detection fallback

## The idea

Add an avrdude-based MCU-detection fallback to `firestarter_app/firestarter/firmware.py` so the host CLI can flash the right firmware even when the device's firmware handshake fails (blank chip, pre-1.0 firmware, wrong firmware previously flashed). Today the install flow requires the device to handshake and self-report its `board` string — no handshake means no install.

## Empirical basis (bench-verified 2026-05-21)

`avrdude` requires `-p <partno>` to launch and cannot answer "what's connected?" in isolation, BUT if you pass the **wrong** `-p`, avrdude reads the chip signature from the bootloader on connect and names the actual part in stderr:

```
$ avrdude -c urclock -P /dev/ttyUSB0 -b 115200 -p m328p -n
avrdude error: connected part ATmega328PB differs in signature from -p ATmega328P
                              ^^^^^^^^^^^^^ ← regex anchor
```

Verbose mode also prints `(probably mXXX)`:

```
$ avrdude -c urclock -P /dev/ttyUSB0 -b 115200 -p m328pb -n -v
avrdude: device signature = 0x1e9516 (probably m328pb)
```

Either parse path works. Confirmed live on the operator's 328PB-Uno (`/dev/ttyUSB0`, Urclock bootloader).

## Why deferred (not Phase 23 / not v1.5)

- The happy path — device handshakes, reports `board: uno328pb`, host flashes `firestarter_uno328pb.hex` — already works end-to-end at the firmware layer (Phase 23 D-15 + bench validation 2026-05-21).
- Adding detection now would expand v1.5 scope beyond the milestone's "third board target" framing. CONTEXT D-11 (Phase 23) explicitly bounded the edit surface to one elif branch + argparse widening.
- This is a v1.6+ "recovery / diagnostics" feature, not a "third board" feature.

## Sketch (for whoever picks this up)

```python
def detect_mcu_via_avrdude(port: str, programmer: str = "urclock", baud: int = 115200) -> Optional[str]:
    """Probe the connected MCU via avrdude. Returns lowercase partno (e.g. 'atmega328pb') or None."""
    result = subprocess.run(
        ["avrdude", "-c", programmer, "-P", port, "-b", str(baud), "-p", "m328p", "-n"],
        capture_output=True, timeout=10
    )
    stderr = result.stderr.decode("utf-8", errors="replace")
    # Route 1: "connected part ATmega328PB differs in signature"
    m = re.search(r"connected part (\w+)", stderr)
    if m:
        return m.group(1).lower()
    # Route 2: "device signature = 0xNNNNNN (probably mXXX)"
    m = re.search(r"\(probably (m\w+)\)", stderr)
    if m:
        return m.group(1)
    return None
```

Then a `firestarter fw -i --detect-mcu` flag would call this when the firmware handshake fails, map the partno back to a board name, and proceed with the matching `.hex`.

## Two real scenarios this unlocks

1. **Blank-chip / pre-1.0-firmware recovery** — operator has a virgin 328PB-Uno with only the Urclock bootloader. Today: `firestarter fw -i` bails because handshake fails. With detection: probe → `atmega328pb` → flash `firestarter_uno328pb.hex` → done.
2. **Wrong-firmware diagnostic** — operator accidentally flashed `firestarter_uno.hex` onto a 328PB. Handshake reports `uno` (the firmware's `RURP_BOARD_NAME` literal), but the silicon is 328PB. Today: host obediently re-flashes `firestarter_uno.hex`, leaving the diagnostic gap intact. With detection: compare handshake-board vs probed-MCU, warn on mismatch.

## Open questions for the eventual implementer

- Which programmers besides `urclock` does this work with? `arduino` (stk500v1) probably reports signature too — needs probing per-board.
- Where to put the partno → board-name reverse map? `(atmega328p → uno, atmega32u4 → leonardo, atmega328pb → uno328pb)` — could live in `firmware.py` constants or as a mirror of the existing forward map.
- UX: silent fallback vs explicit `--detect-mcu` flag? Probably explicit — silent fallback could mask real handshake bugs.

## Cross-references

- Phase 23 CONTEXT D-15: defers real-silicon verification to Phase 24 (now bench-validated 2026-05-21)
- Phase 23 D-11: bounds Phase 23 edit surface; this idea is explicitly outside that surface
- Memory `project-bench-findings-v15`: operator's specific bootloader is Urclock @ 115200
- `firestarter_app/firestarter/firmware.py:_install_with_avrdude` — the function this would extend

## 2026-08-27 annotation (v1.34 Phase 160)

Phase 160 (v1.34, RIG — Dual-Arm Build, Flash Provenance & the Shared Cell Procedure) reused
this idea's bench-verified avrdude signature-probe mechanism (the deliberately-wrong-`-p`
route and the verbose `(probably mXXX)` fallback route described above) in a **phase-owned
rig tool**, `.planning/milestones/v1.34-artifacts/tools/probe_board.py` — RIG-02's "board identity by signature,
never by handshake" requirement is built directly on the two parse routes sketched in this
todo. This is mechanism reuse only: the tool lives under the meta-repo's own
`.planning/milestones/v1.34-artifacts/tools/`, is invoked by this milestone's bench procedure, and is never
imported by or copied into `firestarter_app/`.

This phase does **not** build this todo's product deliverable — a `firestarter fw -i
--detect-mcu` flag in `firestarter_app/firestarter/firmware.py` — because that would be a
product-code change untraceable to a v1.33-caused regression, and `REQUIREMENTS.md`'s Out of
Scope table forbids exactly that class of change for this milestone. This todo's `status` and
`resolves_phase` fields are left unchanged by this annotation: the product-side flag remains
unbuilt and unowned by any phase.
