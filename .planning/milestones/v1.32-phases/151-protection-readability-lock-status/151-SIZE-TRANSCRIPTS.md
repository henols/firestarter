# Phase 151 Plan 10 — Cold Size-Measurement Transcript

**Purpose:** the cold, authoritative measurement Task 1 of plan 151-10 was required to produce
before any exemption literal was touched. Every figure in `firestarter/scripts/check_size_baseline.py`'s
new `MERGE05_LOCK_STATUS_READ_EXEMPTION_BYTES` comment block is read from this document, not
guessed or copied from a planning document.

## 1. Command sequence, per env, in order

For each AVR target, the checker's `--rebuild` path was deliberately **not** used (it runs
`pio run -t clean` first, a warm-cache shape). Instead, exactly:

```
cd /workspaces/firestarter
rm -rf .pio/build/uno
pio run -e uno
rm -rf .pio/build/uno328pb
pio run -e uno328pb
rm -rf .pio/build/leonardo
pio run -e leonardo
```

Then, from the same tree (native envs also `rm -rf`'d first, one invocation per env, so the
warning-watermark figures below are true cold figures too — see §5):

```
rm -rf .pio/build/native
pio test -e native
rm -rf .pio/build/native_nodevtools
pio test -e native_nodevtools
rm -rf .pio/build/native_pinmap_provisional
pio test -e native_pinmap_provisional
```

All six invocations exited 0.

## 2. `Flash:`/`RAM:` lines reported, per env (verbatim)

```
uno:
RAM:   [========  ]  76.9% (used 1575 bytes from 2048 bytes)
Flash: [========  ]  77.6% (used 25418 bytes from 32768 bytes)

uno328pb:
RAM:   [========  ]  77.2% (used 1581 bytes from 2048 bytes)
Flash: [========  ]  77.7% (used 25468 bytes from 32768 bytes)

leonardo:
RAM:   [========  ]  78.8% (used 2016 bytes from 2560 bytes)
Flash: [========  ]  83.9% (used 27500 bytes from 32768 bytes)
```

## 3. Deltas against both baselines, both axes, per env

**BASE-01** (`scripts/baseline/size_baseline_base01.json`, frozen growth axis, cited by path not
re-derived): uno `flash_used=24824`/`ram_used=1573`; uno328pb `24874`/`1579`; leonardo
`26906`/`2014`. These are the same figures a7w's committed cold captures record at
`.planning/quick/260820-a7w-make-the-flash-limit-guards-to-be-the-ac/260820-a7w-cold-{uno,uno328pb,leonardo}.log`,
transcribed there, not re-derived here.

**Pre-151 live baseline** (`scripts/baseline/size_baseline.json` as it read before this plan,
the post-a7w figures): uno `25130`/`1575`; uno328pb `25180`/`1581`; leonardo `27212`/`2016`.

| env | measured flash | measured RAM | Δ flash vs BASE-01 | Δ RAM vs BASE-01 | Δ flash vs pre-151 live (P151's own growth) | Δ RAM vs pre-151 live |
|---|---:|---:|---:|---:|---:|---:|
| uno | 25418 | 1575 | +594 | +2 | +288 | +0 |
| uno328pb | 25468 | 1581 | +594 | +2 | +288 | +0 |
| leonardo | 27500 | 2016 | +594 | +2 | +288 | +0 |

**Existing effective allowance before this plan:** uno-class (uno, uno328pb) `64 + 96 + 210 = 370`
B; leonardo `0 + 96 + 210 = 306` B. Both are short of the measured `+594` B delta against BASE-01
(uno-class short by `594 - 370 = 224`; leonardo short by `594 - 306 = 288`), confirming a third
flash exemption is required, and confirming its value: `+288` B — Phase 151's own flash growth,
identical on all three targets, exactly closing leonardo's shortfall and leaving uno-class with
its usual extra 64 B of headroom (`658 - 594 = 64`).

**RAM finding, stated plainly:** the RAM delta against BASE-01 is `+2` B on all three targets,
identical to what it was before this plan (`+2` against the pre-151 live baseline's own `+2`
carried forward — i.e. **Phase 151's own RAM growth is `+0`**). The existing
`MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES = 2` (Phase 149) already covers the entire `+2` B
delta with zero bytes to spare. **No second RAM exemption is authored.** A funded-but-unneeded
RAM exemption would be exactly the laundering these clauses exist to prevent, and Phase 151 moved
RAM by zero bytes on every target.

## 4. Firmware commits accounting for the growth

All in `firestarter/`, landed after the `260820-a7w` quick task (the tree the pre-151 live
baseline was measured against) and before this plan:

| SHA | Plan | One-line description | AVR flash contribution |
|---|---|---|---|
| `32c32e7` | 151-03 | `feat`: add `CMD_LOCK_STATUS = 16`, widen the memory-command admission gate (`is_memory_cmd()`'s ninth case, the parse-gate widening at `firestarter.cpp`) | yes |
| `4df96c1` | 151-03 | `test`: move both native mirror suites (`test_cmd_admission.cpp`, `test_pinmap_provisional.cpp`) to nine admitted commands | test-only; 0 B AVR (native-only sources, excluded from the AVR `src_filter`) |
| `f66d817` | 151-05 | `feat`: regenerate `messages.h` with `MSG_DATA_PROTECTION_STATUS` (0xE1) | yes (new catalog id's PROGMEM string + `LOG_DATA_ID_BYTES` call site) |
| `6295112` | 151-03 | `test`: re-pin two C-14 consumer sites shifted by the OD-3 comment block | test-only; 0 B (line-number re-pin, no new code) |
| `8db7e55` | 151-08 | `feat`: shared AMD/JEDEC ID-mode read (`flash_util_read_in_id_mode`) + pinned, cited protection-sequence constants for both `0x06`/`0x05` families | yes |
| `0444b1c` | 151-08 | `feat`: `CMD_LOCK_STATUS` read operations (`flash_nor_unlock_read_protection_execute`, `flash_5v_page_read_protection_execute`) and their dispatch arms | yes |
| `3ff9f34` | 151-08 | `feat`: `loop()`'s `CMD_LOCK_STATUS` arm, `eprom_lock_status`, native legs for both families | yes (op-layer glue: `eprom_lock_status` + the `loop()` arm; native-leg additions are test-only) |

## 5. Itemised byte inventory — what the +288 B are

Ten items, matching the plan's own enumeration, with an explicit zero-byte note where measured
at zero:

1. **The widened parse gate** (`is_memory_cmd(handle->cmd) || handle->cmd < CMD_READ_VPP`,
   `firestarter.cpp`) — `32c32e7`.
2. **`is_memory_cmd()`'s ninth admitted case** (`CMD_LOCK_STATUS`) — `32c32e7`.
3. **`flash_util_read_in_id_mode(handle, address)`** — the shared AMD/JEDEC ID-mode single-byte
   read beside `flash_util_get_chip_id` — `8db7e55`.
4. **A new `byte_flip_t` table — measured at ZERO bytes.** Neither family needed one: both the
   `0x06` and `0x05` mode entry/exit sequences reuse the pre-existing `FLASH_ENABLE_ID` /
   `FLASH_DISABLE_ID` tables verbatim (151-08-SUMMARY's explicit finding, transcribed from
   `151-SEQUENCES.md`). Nothing was added here.
5. **Pinned, cited sequence/decode constants**: `FLASH_NOR_UNLOCK_PROTECT_VERIFY_ADDR` /
   `_UNPROTECTED` / `_PROTECTED` (0x06 family) and `FLASH_5V_PAGE_BOOT_BLOCK_STATUS_ADDR` /
   `_UNLOCKED` / `_LOCKED` (0x05 family) — `8db7e55`.
6. **The two `*_read_protection_execute` functions** (`flash_nor_unlock_read_protection_execute`,
   `flash_5v_page_read_protection_execute`) — `0444b1c`.
7. **The two dispatch arms** (one `CMD_LOCK_STATUS` arm per family, each modelled on the existing
   `CMD_CHECK_CHIP_ID` query arm) — `0444b1c`.
8. **`eprom_lock_status`** (`eprom_operations.{h,cpp}`) — `3ff9f34`.
9. **`loop()`'s `CMD_LOCK_STATUS` arm** — `3ff9f34`.
10. **The new catalog id's entry** (`MSG_DATA_PROTECTION_STATUS = 0xE1`, its PROGMEM string and
    the `LOG_DATA_ID_BYTES` emission site) — `f66d817`.

**Also measured at zero, and noted for completeness:** the decision recorded in a code comment
against emitting the pre-existing `MSG_WARN_FL4_BOOT_BLOCK_LOCKED` (0x85) on the 0x05
reads-as-locked branch — nothing was emitted, so nothing was compiled beyond the comment itself.

Sum of the nine nonzero items above measures at exactly `+288` B on all three AVR targets
(uno, uno328pb, leonardo alike) — no target-specific variation was observed, matching the pattern
every prior MERGE-05 exemption in this file has shown (a change gated behind `-D DEV_TOOLS`,
which is inherited by all three AVR envs per `platformio.ini:26`, costs the same bytes on every
target regardless of chip).

## 6. Native-env test summaries (cold)

All three re-measured cold (`rm -rf .pio/build/<env>` then exactly one `pio test -e <env>`
invocation each):

| env | cases | succeeded | suites | all_passed |
|---|---:|---:|---:|---|
| native | 163 | 163 | 17 | true |
| native_nodevtools | 163 | 163 | 17 | true |
| native_pinmap_provisional | 11 | 11 | 1 | true |

These move from the pre-151 recorded `native`/`native_nodevtools` figures of `151 cases / 17
suites` to `163 cases / 17 suites` (suite count unchanged; case count +12, from plan 151-03's
native-mirror-suite growth (`test_cmd_admission.cpp`) and plan 151-08's five new legs in each of
`test_val_nor_unlock.cpp` and `test_val_5v_page.cpp`). `native_pinmap_provisional`'s `11 cases /
1 suite` is unchanged from the figure 151-08-SUMMARY already recorded (that env's own single
suite, `test_pinmap_provisional`, gained its ninth per-command case in plan 151-03, before this
plan started).

## 7. Warning watermarks (cold, re-measured — see the orchestrator's constraint on this)

Run against the same six cold logs, via `check_build_warnings.py`:

```
PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0),
      leonardo: macro_redefinition=0 (== 0), native: total warnings=1166 (== watermark 1166),
      native_nodevtools: total warnings=1166 (== watermark 1166),
      native_pinmap_provisional: total warnings=138 (== watermark 138)
```

All three AVR targets: exactly 0 macro-redefinition warnings. Both pinned native envs land
exactly on the recorded 1166 cold watermark (zero headroom, as documented — a warm re-run of
the same tree measures 998, which must never be mistaken for the cold figure). No watermark in
`size_baseline.json` needed re-recording; none moved.

## 8. The three leonardo figures, kept apart

| figure | value | fails how | guarded? |
|---|---:|---|---|
| MERGE-05 flash band (this plan's new effective allowance: `0 + 96 + 210 + 288 = 594` B) | **594 B**, delta exactly at the ceiling (0 B headroom) | loudly — `check_size_baseline.py --policy merge05` goes red past this | **yes** |
| **Caterina-safe growth budget** | `28672 − 27500 = 1172 B` | **silently — bricks USB bootloader entry on this board** | **no. deliberately none (T-a7w-01).** |
| reported physical `flash_free` | `32768 − 27500 = 5268 B` | — | meaningless as a budget: 4096 B of it *is* Caterina, forfeited by quick task `260820-a7w`, not new flash |

**The operative ceiling for this plan's exemption is the MERGE-05 flash band** (594 B, the one
`--policy merge05` enforces). **The operative ceiling for whether the board still boots over USB
is the Caterina-safe growth budget** (1172 B remaining, unguarded by any checker in this
repository). Both are satisfied; neither is confused with the other; and `flash_free` names
neither.

**For continuity with the pre-151 record:** before this plan's own +288 B landed, leonardo's
Caterina-safe growth budget stood at `28672 − 27212 = 1460 B` and its reported physical
`flash_free` stood at `32768 − 27212 = 5556 B` (both figures already recorded in
`size_baseline.json`'s `meta.deltas_vs_base01.leonardo.merge05_clause` and in 151-DESIGN.md's
objective). This plan's own +288 B growth moves both: the Caterina budget from 1460 B to 1172 B,
and `flash_free` from 5556 B to 5268 B. Neither the 1460/5556 pair nor the 1172/5268 pair should
ever be read as the MERGE-05 flash-band figure (594 B) above — the three axes stay apart.

## 9. Caterina check (T-151-77)

```
28672 - 27500 = 1172   (UNGUARDED -- no gate in this repository checks this figure)
```

`--policy merge05` measures growth against BASE-01 and `platformio.ini` reports leonardo's total
as 32768, so a build that grows past 28672 B would pass every checker in this repository while
having linked over Caterina, the USB bootloader (T-a7w-01, deliberately no compensating guard).
Measured leonardo `flash_used` is **27500 B ≤ 28672 B** — **no overshoot**. This is a
STOP-and-report condition that did not trigger; no bootloader-safe guard was added, and none was
needed.

## 10. Summary of findings this transcript funds

- A third, named, SHA-attributed flash exemption of **288 B**, identical on all three AVR
  targets, funds Phase 151's own firmware growth (items 1-3, 5-10 above). It is added
  alongside, never folded into, the existing 64/96/210 B literals or the unnamed leonardo `band =
  0` inline literal.
- **No second RAM exemption is authored.** Phase 151's own RAM growth measured at exactly 0 B on
  all three targets; the pre-existing `+2` B delta against BASE-01 (Phase 149's page-size seam)
  is unchanged and remains fully covered by `MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES = 2`.
- Leonardo's Caterina-safe margin is **1172 B, unguarded**, and did not overshoot.
- Native-env case counts moved to `163`/`163`/`11` (suites unchanged at `17`/`17`/`1`); warning
  watermarks are unchanged, measured cold, at their recorded zero-headroom figures.
