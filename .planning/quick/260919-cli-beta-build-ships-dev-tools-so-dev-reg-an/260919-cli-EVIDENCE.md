# 260919-cli — Dev-tools oracle validation and AVR flash measurements

Measured 2026-09-19 on `/workspaces/firestarter_fw`, branch `v1.40-program-parameter-fidelity`,
HEAD carrying firmware commit `7eed3af` (`dt_set_registers` re-entrancy fix). All six local
builds ran via `pio run -e <env>`, plain first then with `PLATFORMIO_BUILD_FLAGS="-D DEV_TOOLS=1"`
second, so the build tree left behind at the end of this task is the dev-tools one. `.pio` was
never deleted between runs; PlatformIO rebuilt on the flag-set change alone.

## bootloader-guard lines (verbatim)

Plain build (no extra flags):

```
bootloader-guard: uno 21680/32256 B (67.2% of the safe ceiling, 10576 B margin, 512 B bootloader reserved)
bootloader-guard: uno328pb 21724/32384 B (67.1% of the safe ceiling, 10660 B margin, 384 B bootloader reserved)
bootloader-guard: leonardo 23798/28672 B (83.0% of the safe ceiling, 4874 B margin, 4096 B bootloader reserved)
```

Dev-tools build (`PLATFORMIO_BUILD_FLAGS="-D DEV_TOOLS=1"`):

```
bootloader-guard: uno 22838/32256 B (70.8% of the safe ceiling, 9418 B margin, 512 B bootloader reserved)
bootloader-guard: uno328pb 22882/32384 B (70.7% of the safe ceiling, 9502 B margin, 384 B bootloader reserved)
bootloader-guard: leonardo 24936/28672 B (87.0% of the safe ceiling, 3736 B margin, 4096 B bootloader reserved)
```

No target came within any margin-of-concern of its safe ceiling. Leonardo, the tightest of the
six, still carries 3736 B margin (87.0% of ceiling) under dev tools. No ceiling breach occurred;
no ceiling was raised, no guard relaxed, no env excluded.

## Local build table

| Env | Configuration | Program bytes | Safe ceiling | Margin | Needle (`CTRL remapped`) |
|-----|---------------|---------------:|--------------:|--------:|:--------------------------:|
| uno | plain | 21680 | 32256 | 10576 | absent |
| uno | `-D DEV_TOOLS=1` | 22838 | 32256 | 9418 | present |
| uno328pb | plain | 21724 | 32384 | 10660 | absent |
| uno328pb | `-D DEV_TOOLS=1` | 22882 | 32384 | 9502 | present |
| leonardo | plain | 23798 | 28672 | 4874 | absent |
| leonardo | `-D DEV_TOOLS=1` | 24936 | 28672 | 3736 | present |

Oracle method: for each of the six `.pio/build/<env>/firestarter_*.elf` files, `strings` output
was written to a file (never piped directly into `grep`, per the SIGPIPE/141 hazard noted at
planning time), then that file was searched with `grep -Fq -- 'CTRL remapped'`. This needle
exists only in `src/dev_tools.cpp` and was chosen over the translation-unit name `dev_tools`
itself, which planning-time testing showed present in the ELF even when the guarded code is
compiled out (a linked-but-empty TU still leaves its object's symbol/string table entries).

Result: 3/3 dev-tools builds carry the needle, 0/3 plain builds carry it. The oracle
discriminates cleanly in both directions — it is not a check that would pass regardless of
configuration.

Summary lines:

```
DEVTOOLS_MARKER_IN_DEVTOOLS_BUILD = 3/3
DEVTOOLS_MARKER_IN_PLAIN_BUILD = 0/3
```

## Published `3.0.0b31` release assets — independent confirmation

Fetched with `XDG_CACHE_HOME` pointed at a writable scratch directory:
`gh release download 3.0.0b31 -R henols/firestarter_fw --pattern "*.hex"`.

Each AVR `.hex` was decoded from Intel HEX to raw bytes with a standalone Python decoder handling
record types `00` (data), `02` (extended segment address) and `04` (extended linear address), and
the decoded byte string was searched for the same needle, `CTRL remapped`, using plain Python
substring containment (no `strings`/ELF involved — these are already-linked raw program images,
not object files).

| Asset | Decoded program bytes | Needle present |
|-------|------------------------:|:----------------:|
| `firestarter_uno.hex` | 22734 | yes |
| `firestarter_uno328pb.hex` | 22778 | yes |
| `firestarter_leonardo.hex` | 24830 | yes |

These figures match the planning-time context block exactly (22734 / 22778 / 24830 B), confirming
the published `3.0.0b31` pre-release genuinely ships all three AVR images built with dev tools
compiled in. They differ from this task's own local dev-tools byte counts (22838 / 22882 / 24936)
by roughly 100 B per target — expected, since the published build ran through the full
`beta-build.yml` pipeline (its own version-string length, toolchain snapshot, and CI environment)
rather than this local `pio run` invocation; the needle-presence property is what both builds are
being compared on, not byte-for-byte identity.

```
DEVTOOLS_MARKER_IN_PUBLISHED_B31 = 3/3
```

## Conclusion

The oracle (`strings` output on a linked AVR ELF, or a plain substring search on a decoded `.hex`
image, for the literal `CTRL remapped`) discriminates a `-D DEV_TOOLS=1` build from a plain build
with zero false positives and zero false negatives across six local builds, and independently
confirms the published beta pre-release ships dev tools on all three AVR targets. This is the
needle Task 2's CI assertions use.
