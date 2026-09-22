---
title: FWBLANK-05 flash/RAM measurement record — v1.41 Phase 205
phase: 205-the-pre-flights-leave-the-firmware
plan: "02"
measured: 2026-09-22
status: phase-entry baseline is AUTHORITATIVE; phase-exit is EMPTY, filled by plan 06 on the
  post-sweep tree
requirements: [FWBLANK-05]
---

# FWBLANK-05 — flash and RAM measurement record

Every number below carries the command that produced it, measured on this machine at
`firestarter_fw` commit `a4e002f2da0b44e7545ab43180951538e64022c1`, on branch
`v1.41-verification-to-host`. Nothing here is copied from `205-RESEARCH.md`'s simulation —
the research's own simulated-sweep figures happen to match this baseline exactly (same
tree, same toolchain, no firmware source touched between the research session and this
plan), which is itself evidence the two runs measured the same thing rather than a
substitute for measuring it again here.

---

## Build configuration, stated rather than assumed

CONTEXT D-10 states three build-configuration premises. Measurement corrects all three:

- **`DEV_TOOLS` is 0 on all three AVR targets, not "on by default."**
  `firestarter_fw/include/firestarter.h:31-33`:
  ```c
  #ifndef DEV_TOOLS
  #define DEV_TOOLS 0
  #endif
  ```
  `-D DEV_TOOLS=1` appears only in `platformio.ini`'s `[env:native]` (line 140). None of
  `[env:uno]`, `[env:uno328pb]` or `[env:leonardo]` set it, and none extend an environment
  that does. The three AVR targets measured below are non-`DEV_TOOLS` builds.

- **`SERIAL_DEBUG` is commented out in `[env] build_flags`, not `DEV_TOOLS`-gated.**
  `platformio.ini:22`: `; -D SERIAL_DEBUG` (the leading `;` disables it). Every
  `LOG_DEBUG_ID_SUB*` macro in `firestarter_fw/include/logging_id.h:314-326` expands to
  nothing without it (the `#else // !SERIAL_DEBUG — production no-op fallback` branch).
  `firestarter.cpp:89`'s `DBG_FLAG_SKIP_BLANK` emit site — one of the D-09 sweep sites —
  therefore contributes **zero bytes** to any of the three shipped AVR images.

- **`SERIAL_ON_IO` is defined for `uno` and `uno328pb` only, and does not appear in
  `memory.cpp`.** `platformio.ini:38` (`[env:uno]`) and `:53` (`[env:uno328pb]`) define it;
  `[env:leonardo]` does not. `git grep SERIAL_ON_IO -- src/ include/` returns hits only in
  `rurp_shield.h`, `eprom_operations.cpp` and `eprom.cpp` — none in `memory.cpp`, the file
  the blank-check sweep touches. CONTEXT D-10's prediction that the per-target deltas "will
  legitimately differ" because of `SERIAL_ON_IO` does not apply to this phase's removal:
  the sweep's own code lives entirely outside the `SERIAL_ON_IO`-gated block.

These three corrections are why an **identical** per-target delta is the expected outcome of
the coming sweep (plan 06), not a surprise to explain away.

No CI leg gates image size. `firestarter_fw/scripts/` carries no `check_size_baseline.py`
and no `size_baseline.json` exists anywhere in the repository (confirmed: `ls scripts/`
shows only `check_cmake_manifest.py`, `check_erase_no_vpp.py`, `check_landing_range.py` and
`check_orphan_provisional.py`; the only trace of the old script is a stale `__pycache__`
artifact). This record is a measurement, not an enforced pass.

---

## Phase-entry baseline

Method: `pio run -t clean -e <env>` individually for `uno`, `uno328pb` and `leonardo`, then
one `pio run -e uno -e uno328pb -e leonardo`, reading each target's `Flash:`/`RAM:` summary
line. Reproduced a second time (full clean + rebuild) with byte-identical output before
recording.

```bash
cd /workspaces/firestarter_fw
pio run -t clean -e uno && pio run -t clean -e uno328pb && pio run -t clean -e leonardo
pio run -e uno -e uno328pb -e leonardo
```

| Target | Flash used | of | % | margin | RAM used | of | % | margin |
|---|---|---|---|---|---|---|---|---|
| `uno` | **21452** B | 32768 | 65.5% | 11316 B | **1398** B | 2048 | 68.3% | 650 B |
| `uno328pb` | **21496** B | 32768 | 65.6% | 11272 B | **1404** B | 2048 | 68.6% | 644 B |
| `leonardo` | **23810** B | 32768 | 72.7% | 8958 B | **1839** B | 2560 | 71.8% | 721 B |

**Leonardo against its real ceiling (both denominators quoted, per the Phase 201 note's
form):** 23810 / 32768 = **72.7%** (8958 B margin, the `platformio.ini`-reported figure) =
23810 / 28672 = **83.04%** (**4862 B of true margin**) against the real
ATmega32U4-on-Caterina ceiling — `platformio.ini`'s `board_upload.maximum_size = 32768`
override means the linker no longer protects the top 4096 B that Caterina actually needs.
`.planning/notes/201-region-blank-check-latency-and-divergence.md` § 3 recorded 24134 B
(84.2%, 4538 B margin) at that phase's close; Phase 204's removal freed 324 B between then
and this baseline (24134 − 23810 = 324).

### Artifact digests

```bash
for e in uno uno328pb leonardo; do
  for x in elf hex; do sha256sum ".pio/build/$e/firestarter_$e.$x"; done
done
```

| Target | `.elf` sha256 | `.hex` sha256 |
|---|---|---|
| `uno` | `046dac09ccd6f2b8ecb7c770f928700d86dde638797aa555a1a87234c587aea0` | `663a65bc0de129e72692af8a063a9f4a7193c3ccae049f0214ccc3a9c0231d1d` |
| `uno328pb` | `d3f9fc5e20ed2fbdd30012986a627007742e715723baad30888804136b628d07` | `e784f2b90f3eb49f41fdf2e6d525cbf49f440706e28dca9793222d12130402c2` |
| `leonardo` | `6d8771d226f8db869d67d272ca5a47c11e177f5fd541558915fd9633e256ac5b` | `8beeb731831d04347c75528bebe2a7cdc04e1eeb1d3da76a3933dc8809ec710b` |

Both `pio run` invocations (the initial measurement and the reproduction) produced these
same six digests and the same six `Flash:`/`RAM:` lines, character for character.

---

## Phase-exit

*Empty. Plan 06 fills this section from a clean `pio run -t clean` + `pio run` on the
post-sweep tree, after every FWBLANK-01 through FWBLANK-04 removal has landed. Plan 05's
negative-address fix (the folded firmware half of
`2026-09-16-reject-negative-write-start-address.md`) is measured as its own line here if it
lands before plan 06, so the sweep's own delta stays separable from a fix that adds code
rather than removes it.*

| Target | Flash used | of | % | RAM used | of | % |
|---|---|---|---|---|---|---|
| `uno` | — | — | — | — | — | — |
| `uno328pb` | — | — | — | — | — | — |
| `leonardo` | — | — | — | — | — | — |

Leonardo double-denominator (32768 / 28672): — / —

### Artifact digests

| Target | `.elf` sha256 | `.hex` sha256 |
|---|---|---|
| `uno` | — | — |
| `uno328pb` | — | — |
| `leonardo` | — | — |

## Delta

*Empty. Plan 06 computes phase-exit minus phase-entry per target, per FWBLANK-05.*

---

## Provenance

| Field | Value |
|---|---|
| `firestarter_fw` commit at which the baseline was taken | `a4e002f2da0b44e7545ab43180951538e64022c1` |
| Branch | `v1.41-verification-to-host` |
| Date measured | 2026-09-22 |
| PlatformIO Core version | 6.2.0 |
| `toolchain-atmelavr` | 1.70300.191015 |
| `framework-arduino-avr` | 5.3.0 |
| `framework-arduino-avr-minicore` (uno328pb) | 3.1.2 |
| `git status --porcelain` in `firestarter_fw` after the build | empty |

No CI leg gates image size: `firestarter_fw/scripts/baseline/size_baseline.json` and
`check_size_baseline.py` are cited by four firmware test modules and do not exist in this
repository. This record exists because FWBLANK-05 asks for a measurement, not because any
gate enforces one.
