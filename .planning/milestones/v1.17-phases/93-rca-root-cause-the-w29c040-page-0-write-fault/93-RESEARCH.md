# Phase 93: RCA — Root-Cause the W29C040 Page-0 Write Fault - Research

**Researched:** 2026-06-26
**Domain:** Firmware root-cause analysis — AMD/JEDEC page-write flash (W29C040, protocol 0x05 "flash4"); differential silicon isolation; AVR bus-timing; SDP unlock sequences
**Confidence:** HIGH (firmware verified by direct source read; W29C040 + W29C020 datasheets present in-repo and extracted; prior bench failure signature recorded verbatim)

> This is a **diagnosis** phase, not a fix phase. Every finding below is framed to let Phase 94
> design a *targeted* fix. Where the research points at a likely cause, it is stated as a
> **ranked hypothesis with a disconfirming test**, never as a settled fix recommendation.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| RCA-01 | Reproduce the W29C040 page-0 write fault on the seated chip with a captured failure signature (which addresses/bytes fail, DQ7/DQ6 toggle-poll behavior) | §Reproduction & Signature Capture — exact prior signature (`Timeout verifying 0xd7 at 0x0000ff (got 0x00)`); the `write -b` repro command; the `DEBUG_ADDRESS` build-flag trace path; `dev` instrumentation surface (`dev write-cycle`, `dev reg`, `dev addr`, `dev read`) that captures the signature with no escape hatch |
| RCA-02 | Differentially compare W29C040 vs the passing sibling W29C020 across the 4 candidate axes (SDP unlock, page-write polling/timing, A18 512KB addressing, page size) and isolate the differing variable(s) | §Differential Method — datasheet-grounded axis-by-axis table (both datasheets extracted); the ONE differing line (A18) + the page-size delta (256B vs 128B) + the T_BLC byte-load window; firmware branch points where capacity/address-width matters |
| RCA-03 | Record a named root cause (or ranked hypotheses each with disconfirming evidence), classified firmware-algorithm / timing / addressing / silicon, sufficient to design a fix | §Root-Cause Classification — 5 ranked hypotheses, each with a STRIDE-style classification + a concrete disconfirming bench test |
| SAFE-01 | Over-voltage stays blocked at the firmware VPP check; host `chip_resolver.resolve_chip` guard never bypassed; W29C040 flows through normal dispatch, no test-only escape hatch | §Safety & Instrumentation Boundaries — all RCA instrumentation uses the normal `0x05` dispatch path + existing `dev` commands; `DEBUG_ADDRESS` is a passive trace, not a dispatch escape; flash4 write path provably sets NO VPP control bits (verified) |
</phase_requirements>

---

## User Constraints

> No `93-CONTEXT.md` exists yet — this RESEARCH.md was produced standalone (pre-discuss). The
> constraints below are the **locked milestone context** from STATE.md / REQUIREMENTS.md /
> ROADMAP.md and the operator's standing bench discipline. They bind the planner exactly as a
> CONTEXT.md would. If `/gsd-discuss-phase 93` runs later, its CONTEXT.md supersedes this section.

### Locked Decisions (from STATE.md / REQUIREMENTS.md / ROADMAP.md)
- **This is RCA only.** Deliverable = reproduced signature + differential isolation + named root cause (or ranked disconfirmed hypotheses) classified firmware-algorithm/timing/addressing/silicon. **Do NOT design or commit a fix** — that is Phase 94.
- **Page size is ALREADY correct (256 B)** in the current firmware for the W29C040 (`flash4_page_size(524288) → 256`). The page-0 fault root cause is **distinct from** the CR-01 page-size generalization. Do not re-chase page-size as *the* cause; it is confirmed the right value for this chip.
- **Phase-74 Wave-1 fix already tried the obvious candidates** (SDP unlock + 256B page + `CMD_CHECK_CHIP_ID`) — committed at fw `6924349`/`2699d11`, native-green, but proved **NOT silicon-effective** at v1.15 Phase 82 and v1.15 Phase 84 (deterministic FAIL). The RCA must go *deeper* than the Phase-74 hypothesis.
- **Differential control = W29C020** (same protocol 0x05 "flash4", same pinout `DIP32_SST39SF040`, auto-erase EEPROM/Flash, 256 KB / 128 B page). W29C020 **PASSED** the v1.15 A→B auto-erase bench (gold reference).
- **Bench LOCKED to Leonardo + RURP Rev 2.0 + operator-seated W29C040.** Standing discipline: live R1/R2 readback each task (r1 ≈ 270000 ± 25%), verify `controller:` port identity per task, **Leonardo is chip-OUT-sideload-EXEMPT** (do NOT instruct chip removal before sideload for Leonardo). Operator seats the chip so the bench can be driven unattended.
- **SAFE-01:** over-voltage stays blocked at the firmware VPP check; the host `chip_resolver.resolve_chip` guard is never bypassed; the W29C040 flows through its normal `0x05` dispatch — **no test-only escape hatch.**
- **Branch base:** firmware forks off v1.16 tip `a296195` (primitives recompose), NOT firmware `beta`. flash4 lives on the P7/P4/P3/P5 primitives recompose.

### Claude's Discretion
- Which instrumentation knobs to use for the signature capture (`DEBUG_ADDRESS` trace build vs `dev reg`/`dev addr` poking vs serial ERROR-frame decoding) — recommend a method, but the planner/operator chooses at the bench.
- The order in which the 5 ranked hypotheses are disconfirmed (the disconfirming-test matrix can run in any order; cheapest-first is recommended).
- Whether to capture DQ6 toggle-bit behavior in addition to DQ7 data-polling (the firmware polls DQ7 only today; DQ6 capture needs `dev`-level register reads).

### Deferred Ideas (OUT OF SCOPE for Phase 93)
- **Designing/committing the fix** → Phase 94 (FIX-01/02/03).
- **Datasheet-sourced per-chip `page_size` DB field (CR-01 generalization)** → Phase 94 (PGSZ-01/02/03). Phase 93 only needs to *confirm* 256 B is correct for W29C040 and 128 B for W29C020.
- **Bench graduation (byte-exact write→verify SHA gate)** → Phase 95 (BENCH-01/02/03).
- **AM27C020 0x08 (FUT-06), 2516 0x0B (FUT-03)** — unrelated families, deferred.

---

## Summary

The W29C040 (Winbond 512K×8 5V page-write flash, protocol `0x05` "flash4") **deterministically fails its first page program**: prior bench evidence (v1.15 Phase 82 and Phase 84, Leonardo + Rev 2.0) records `ERROR "Timeout verifying 0xd7 at 0x0000ff (got 0x00)"` — the DQ7 poll on the **last byte of page 0 (address `0x0000ff`)** times out, reading back `0x00` (neither the written `0xd7` nor an erased `0xFF`). This is reproducible across reseats. The passing sibling **W29C020** (same `0x05`, same `DIP32_SST39SF040` pinout, 256 KB / 128 B page) writes→auto-erases→verifies clean on the identical bench and firmware build — making it the perfect differential control.

The Phase-74 Wave-1 fix already added the two "obvious" things (SDP unlock `FLASH_ENABLE_WRITE` per-page + data-driven 256 B page) and they are present in the current `flash_type_4.cpp` on the `a296195` recompose — yet the chip still fails. So the cause is **not** "missing SDP" and **not** "wrong page size." The datasheets (both committed in-repo: `datasheets/0x05-FLASH-AMD-STD/W29C040.pdf` and `W29C020.pdf`) narrow the differential to a small set: (a) the **byte-load cycle timing window T_BLC = 200 µs** — if the per-byte AVR load loop ever exceeds it mid-page, the chip prematurely commits the page; (b) the **page-address bits** — W29C040 latches A8–A18 as the page address (256 B page), W29C020 latches A7–A17 (128 B page), so **A18 is the one address line W29C040 exercises that W29C020 never does**; and (c) the interaction between the **SDP unlock writes** (which only touch the LSB/MSB registers + a `CTRL_READ_WRITE` control write, NOT the A16–A18 top-address bits) and the subsequent per-byte data loads (which DO rewrite the full top-address register every byte).

**Primary recommendation:** Reproduce the documented signature first (cheap, deterministic), then run the differential disconfirming-test matrix in cheapest-first order — the strongest single hypothesis is **H1 (byte-load timing window violation, classification = timing)** because the public-domain failure mode for exactly these AMD/JEDEC page-write parts is "programmer loads the page too slowly, chip commits mid-page," and the firmware's per-byte `memory_set_data` path (LSB + MSB + CONTROL register writes + two `delayMicroseconds` calls + CE pulse) is heavier than the single-byte flash3 path that passes — but H1 must be disconfirmed against **H2 (A18/top-address corruption during page load, classification = addressing)** and **H4 (DQ7 poll site / page-commit-not-fired, classification = firmware-algorithm)** before naming a cause.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Reproduce + capture failure signature | Firmware (`flash4_write_execute`, `flash4_wait_for_page_write`) emitting `MSG_ERR_FL4_VERIFY_TIMEOUT` | Host CLI `firestarter write -b` / `dev write-cycle` driving + decoding the ERROR frame | The fault is a firmware page-write-path timeout; the host is the harness that drives it and surfaces the byte-tagged error frame |
| Differential axis isolation | Analysis (datasheet vs firmware source) | Bench (write attempts on W29C040 vs W29C020 silicon) | The axes are decided by reading two datasheets + the handler; bench confirms which axis actually moves the outcome |
| Address-bus / A18 routing during page load | Firmware (`mem_util_set_address` → top-address CONTROL register; `mem_util_remap_address_bus`) | Hardware (Rev 2.0 control-register bit map — `CTRL_ADDRESS_LINE_18_REV2 == CTRL_VPP_P1_ENABLE_REV2 == 0x08`) | A16–A18 are carried in the CONTROL register, not the LSB/MSB registers; the Rev 2.0 bit layout differs from legacy |
| Byte-load timing (T_BLC window) | Firmware (per-byte `memory_set_data` loop cost) | Hardware (16 MHz AVR `delayMicroseconds` accuracy) | The 200 µs inter-byte window is a silicon constraint the firmware loop must satisfy |
| DQ7 data-poll / DQ6 toggle completion detect | Firmware (`poll_readback` P5 primitive, cap=1024) | Bench (observe poll outcome via ERROR frame / `dev read`) | Completion detection is the symptom site; whether the poll is *wrong* or the page *never committed* is the H4-vs-H1 fork |
| Safety (VPP blocked, host guard intact) | Host `chip_resolver.resolve_chip` (in-host refusal) | Firmware VPP check + flash4 write path emits zero VPP control bits | SAFE-01 — instrument without any escape hatch |

---

## Standard Stack

This is an RCA phase on existing firmware — **no new packages are installed.** The "stack" is the in-repo toolchain and the chip datasheets.

### Core (existing tooling — reuse only)
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| PlatformIO (`pio`) | in-repo `platformio.ini` | Build/flash firmware for `leonardo`; run `pio test -e native` | Project-standard build; the `[env:native]` recording-stub suite is the Tier-1 RCA oracle |
| `firestarter` CLI (host) | editable install (`pip install -e .`) | Drive write/read/verify + `dev` instrumentation over serial | Project-standard host; `dev write-cycle`/`dev read`/`dev reg`/`dev addr` already exist |
| `firestarter/src/proms/flash_type_4.cpp` | `a296195` recompose | The code under investigation (`flash4_write_execute`, `flash4_wait_for_page_write`) | The handler that fails |
| `datasheets/0x05-FLASH-AMD-STD/W29C040.pdf` | in-repo (Rev A11, 28 pp) | Authoritative W29C040 page-write/SDP/timing facts | The silicon spec for the failing chip |
| `datasheets/0x05-FLASH-AMD-STD/W29C020.pdf` | in-repo (Rev A3, 21 pp) | Authoritative W29C020 facts for the differential | The silicon spec for the passing control |
| `pypdf` | host Python | Extract datasheet text (no `poppler` in container) | `pdftotext`/`pdftoppm` absent; `pypdf` present and works |

> **STATE.md correction:** STATE.md (line 90) says "no W29C040 datasheet committed yet." This is **stale** — both `W29C040.pdf` and `W29C020.pdf` are present in `datasheets/0x05-FLASH-AMD-STD/` and were extracted for this research. The datasheet-acquisition concern in the objective is resolved; no acquisition is needed for Phase 93.

### Supporting (RCA instrumentation knobs — all already in-tree)
| Knob | Where | Purpose | When to Use |
|------|-------|---------|-------------|
| `DEBUG_ADDRESS` build flag | `firestarter/platformio.ini:25` (commented) | Emits per-address `DBG_ADDRESS` (U24) + `DBG_TOP_MSB_LSB` (top/msb/lsb register triplet) over serial on every `mem_util_set_address` | Passive register-trace build to *see* what A16–A18 are during page load — the H2 disconfirming instrument. Passive trace, NOT an escape hatch (SAFE-01 safe). |
| `dev write-cycle <chip> <img>` | host CLI | Erase→write→read-back N×, 3-way verdict (0/1/2) | Deterministic repro harness for the failure signature |
| `dev read` / `firestarter read` | host CLI | Read back the chip to inspect post-fail state (is page 0 `0x00`, `0xFF`, or partial?) | Characterize what page 0 actually contains after the timeout |
| `dev reg <chip> <lsb> <msb> <ctrl>` | host CLI | Direct LSB/MSB/CONTROL register poke (with remap) | Manual single-byte / SDP-sequence reproduction for the H1/H4 fork (e.g., write one byte to page 0 and poll) |
| `dev addr <chip> <address>` | host CLI | Direct address-line + control-register drive | Confirm A18 actually toggles pin 1 on Rev 2.0 |
| `pio test -e native -f "*test_val_flash4*"` | firmware | Tier-1 recording-stub register-sequence assertions | Confirm the *emitted* SDP/address sequence matches the datasheet WITHOUT silicon (cheap pre-bench check) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `DEBUG_ADDRESS` serial trace | Logic analyzer / scope on the shield bus | Scope is operator-only (hardware), gives ground-truth timing for T_BLC (H1) — but slower to set up; serial trace is unattended-driveable. Recommend serial trace first; escalate to scope only if H1 needs sub-µs timing proof. |
| `dev write-cycle` repro | Raw `firestarter write -b` | `write -b` is the exact command that produced the recorded signature; `dev write-cycle` adds N-run determinism + verdict codes. Use both: `write -b` to match the historical signature, `dev write-cycle` for N≥2 determinism. |
| Native recording-stub | Bench-only | The native stub can't reproduce a *timing* fault (no real silicon clock) but CAN prove the address/SDP *sequence* is datasheet-correct — pair them. |

**Installation:** None. RCA uses the existing editable host install + `pio`. Confirm host install with `firestarter --help` and firmware build with `pio run -e leonardo`.

---

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** The only third-party tool touched is `pypdf` (datasheet text extraction), already present in the container Python and used read-only for research; it is not a runtime dependency of either sub-repo. No `npm`/`pip`/`cargo` install occurs in Phase 93.

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

---

## Architecture Patterns

### System Architecture Diagram — the W29C040 write path under investigation

```
firestarter write -b W29C040 <image>          (host CLI; SAFE-01 in-host guard)
        │
        ▼
chip_resolver.resolve_chip("W29C040")  ──► refuses if not 'supported' (NEVER bypassed)
        │   emits algorithm=5, pinout=DIP32_SST39SF040, vpp_mv=12000, pin-count=32, size=524288
        ▼
eprom_operations.py ──► JSON cmd ──► serial_comm.py (COBS+CRC8, 250000 baud)
        │
        ▼  [FIRMWARE on Leonardo + Rev 2.0]
configure_memory()  ──► protocol==0x05 ──► configure_flash4()        (memory.cpp:116)
        │
        ▼
flash4_write_init()                                                  (flash_type_4.cpp:72)
   ├─ FLAG_CAN_ERASE? → flash4_erase_execute()  ⚠ asserts VPP regulator bits (see Pitfall 3)
   └─ blank_check (unless FLAG_SKIP_BLANK_CHECK)
        │
        ▼
flash4_write_execute()                                               (flash_type_4.cpp:91)
   for each byte i in data_size:
     ├─ is_page_start (addr % 256 == 0) OR is_first_byte?
     │     └─ flash_execute_command(FLASH_ENABLE_WRITE)   ──► SDP: write 0xAA→0x5555,
     │            (flash_util_byte_flipping → fu_flash_fast_address)     0x55→0x2AAA, 0xA0→0x5555
     │            ⚠ writes LSB+MSB registers + CTRL_READ_WRITE ONLY — does NOT
     │              set the A16–A18 top-address CONTROL bits  (H2 hinge)
     ├─ firestarter_set_data(addr, byte)  = memory_set_data            (memory.cpp:346)
     │     └─ mem_util_remap_address_bus + mem_util_set_address
     │            ──► writes LSB, MSB, AND top-address CONTROL (A16–A18)  ← full address every byte
     │            ──► delayMicroseconds(3) + CE pulse + delayMicroseconds(pulse_delay)  (H1 hinge: per-byte cost vs T_BLC=200µs)
     └─ reached_page_end (addr+1 % 256 == 0) OR is_last_byte?
           └─ flash4_wait_for_page_write(addr, expected)              (flash_type_4.cpp:120)
                 └─ poll_readback(addr, expected, max_iters=1024)     (primitives.cpp:70)
                       per-iter: delayMicroseconds(10) + read addr; match DQ-exact (full byte, NOT DQ7-mask)
                       on timeout → MSG_ERR_FL4_VERIFY_TIMEOUT [expected, A16, A8, A0, observed]   (H4 hinge)
                                                                                       │
        ◄──────────────────────────────── ERROR frame ◄──────────────────────────────┘
        "Timeout verifying 0xd7 at 0x0000ff (got 0x00)"   ← THE SIGNATURE
```

### Recommended RCA artifact structure
```
.planning/phases/93-rca-.../
├── 93-RESEARCH.md            # this file
├── 93-CONTEXT.md             # (if /gsd-discuss-phase runs)
├── 93-NN-PLAN.md             # planner output
└── evidence/
    ├── 93-RCA-FINDINGS.md    # canonical named root cause (mirror Phase 44's evidence/44-RCA-FINDINGS.md pattern)
    ├── signature/            # captured ERROR frames + DEBUG_ADDRESS traces + post-fail read-backs
    └── differential/         # W29C040 vs W29C020 paired write attempts + SHAs
```

### Pattern 1: 2×N differential isolation (reuse the Phase 44 method)
**What:** Hold everything constant except ONE axis; flip that axis; observe whether the outcome moves. Phase 44 (Bug A RCA) used a 2×2 controller×shield crossover to isolate a fault to the shield. Phase 93's analog is **W29C040 vs W29C020 on the same board+shield+firmware build**, then **per-axis sub-flips** (single-byte vs full-page write; page-0 vs non-page-0; A18-low vs A18-high address).
**When to use:** Every candidate axis in RCA-02.
**Example:**
```
# Same Leonardo + Rev 2.0 + same fw build for BOTH:
firestarter write -b W29C020 <128K image>   → PASS (control)   ← exonerates code structure
firestarter write -b W29C040 <512K image>   → FAIL @0x0000ff   ← the chip-under-test
# Then sub-flip on W29C040 only:
firestarter write -b W29C040 -a 0 -s 1      → single byte to page 0  (H1/H4 fork)
firestarter write -b W29C040 -a 0x40000     → write a page where A18=1 (H2 probe)
```

### Pattern 2: Disconfirming-first hypothesis testing (Phase 44 D-07 causal bar)
**What:** For each hypothesis, define the observation that would **disprove** it, and run that. A named root cause is one that survives its own disconfirming test while competitors fail theirs. Phase 44's governing bar was "a knob that controls the symptom" — apply the same: a hypothesis is *named* only when a knob predicted by it actually moves the failure.
**When to use:** RCA-03 classification.

### Anti-Patterns to Avoid
- **Re-asserting the Phase-74 hypothesis** ("add SDP / fix page size") — both are already present and proven non-effective. Naming either as the cause without new disconfirming evidence repeats the v1.15 mistake.
- **N=1 bench conclusions** — the standing discipline (and the uno328pb instability lessons) require N≥2 deterministic repro before naming. The recorded signature is already N=2 deterministic; keep that bar.
- **Trusting a native-only PASS as silicon proof** — the Phase-74 fix was native-green and silicon-FAIL. Native tests can only confirm the *emitted sequence*; they cannot confirm *timing* or *silicon acceptance*. The named cause must cite silicon evidence (or a silicon-grounded disconfirming test), not just a passing native suite.
- **Adding a test-only escape hatch** to "make repro easier" — forbidden by SAFE-01. All repro flows through the normal `0x05` dispatch.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Reproduce + record the signature | A new bespoke write-and-diff script | `firestarter write -b` (matches historical signature) + `dev write-cycle` (N-run verdict) | Already exist; `dev write-cycle` gives the 0/1/2 verdict contract the RCA needs |
| See A16–A18 during page load | A custom serial protocol to dump registers | `-D DEBUG_ADDRESS` build flag (emits `DBG_TOP_MSB_LSB`) | Passive, in-tree, SAFE-01-safe; no dispatch change |
| Confirm the emitted SDP/address sequence | Manual reading of disassembly | `pio test -e native -f "*test_val_flash4*"` recording-stub | Tier-1 oracle already asserts the SDP MSB signature + the 2-SDP-per-256B-boundary invariant |
| Single-byte / manual page poke | Firmware special-case | `dev reg` / `dev addr` | Direct register/address drive through the normal handle path |
| DQ7 vs full-byte poll question | Re-derive poll semantics | Read `poll_readback` (primitives.cpp:70) — it compares the **full byte**, not DQ7-masked | The firmware does NOT mask DQ7 in flash4's poll (it does in flash3's `flash_util_verify_operation`). This asymmetry is itself an H4 clue. |

**Key insight:** Every instrument the RCA needs already exists in-tree. The phase's work is *experimental design + interpretation*, not tooling. The one decision is which knob disconfirms which hypothesis fastest.

---

## Reproduction & Signature Capture (RCA-01)

### The recorded signature (prior, verbatim — the pre-fix baseline to reproduce)
From `.planning/v1.15/bench/EVIDENCE.md` (Phase 82 + Phase 84 Task 3c), Leonardo + Rev 2.0, on a firmware build **carrying the Phase-74 SDP/256B-page fix** [VERIFIED: direct read of EVIDENCE.md]:

| Attempt | Result |
|---------|--------|
| Phase 82 write A (`-b`) | `Timeout verifying byte @0x0000ff` (256 B page-0 boundary); reads `0x00` |
| Phase 84 attempt 1 (`-b`, 1024 B image, SHA `9983e8de…`) | `ERROR "Timeout verifying 0xd7 at 0x0000ff (got 0x00)"` |
| Phase 84 attempt 2 | Identical (deterministic N=2) |

**Decoded:** the DQ7/whole-byte poll on **address `0x0000ff` = the last byte of page 0** times out (`poll_readback` exhausts its 1024 iterations). The byte reads back **`0x00`** — *not* the written `0xd7`, and *not* an erased `0xFF`. The error frame payload is `[expected=0xd7, A16=0x00, A8=0x00, A0=0xff, observed=0x00]` (per `flash4_wait_for_page_write` `_b[]` packing, flash_type_4.cpp:128–134).

**Interpretation hooks for RCA-03:** `observed == 0x00` is the load-bearing clue. If the page had erased but not programmed, page 0 would read `0xFF`. `0x00` means **either** (a) the page never entered/committed a write cycle and the address still holds pre-existing `0x00` data, **or** (b) the chip is mid-internal-write and DQ7 is returning the *complement* of the true data during the write cycle (datasheet §6.7: during the internal write, reading the last-loaded address returns the **complement of DQ7**; `0xd7` has DQ7=1, so its complement reads DQ7=0 → a `0x00`-ish read is consistent with "still writing / never completed"). The RCA must distinguish (a) from (b).

### Repro command (matches the historical signature)
```bash
# Standing discipline FIRST: verify controller identity + live R1/R2 readback for THIS port.
firestarter --version            # confirm controller: identity on the seated port
firestarter dev read W29C040 -a 0 -s 16   # (optional) read pre-state of page 0

# Reproduce the signature (deterministic; -b = plain write w/ blank-check; image must cross 0x100):
firestarter write -b W29C040 /tmp/w29c040_img.bin
# expect: ERROR "Timeout verifying 0x.. at 0x0000ff (got 0x00)"

# N≥2 determinism via the dev harness (0=PASS,1=mismatch,2=hw-error):
firestarter dev write-cycle W29C040 /tmp/w29c040_img.bin --runs 2
```
> Generate the image with the repo's `tools/gen_test_image.py <bytes> <seed>` (used in v1.15) so it is deterministic and **crosses the 256/512/768 page boundaries** (≥ 1024 B). The 0x0000ff fault is at the page-0 boundary, so even a 256 B image suffices to trigger it; use ≥1024 B to also observe whether later pages behave.
> ⚠ **`-b` semantics caveat** (see [[reference_write_b_skips_erase]]): in older host builds `-b` set `FLAG_SKIP_ERASE`. v1.16 Phase 92 (HARD-01) **decoupled** `-b`/`--no-blank-check` from skip-erase — pre-write erase still runs for `FLAG_CAN_ERASE` chips; an explicit `--skip-erase` is now required to skip. Confirm the host build is post-HARD-01 so the repro is not a skipped-erase artifact. The W29C040 (Flash/EEPROM) auto-erases per-page on write anyway.

### Signature capture — what to record (RCA-01 deliverable)
1. **The exact ERROR frame** (expected byte, full failing address, observed byte) for ≥2 runs.
2. **Post-fail read-back of page 0** (`firestarter dev read W29C040 -a 0 -s 256`): is it all `0x00`, all `0xFF`, partially programmed, or the pre-existing pattern? This decides hypothesis (a) vs (b) above.
3. **DEBUG_ADDRESS trace** (build firmware with `-D DEBUG_ADDRESS`, sideload — Leonardo is chip-OUT-exempt, leave chip seated): capture the `DBG_TOP_MSB_LSB` triplet emitted for each byte of the page-0 load and for the SDP unlock writes. This shows whether A16–A18 (top register) are what they should be during the load (H2 probe) and lets you *count* the per-byte cadence (H1 probe).
4. **DQ7/DQ6 behavior at the failing address** — via `dev read` of `0x0000ff` repeatedly during/after the fail, observe whether DQ7 toggles (toggle-bit DQ6) or is stuck. The firmware polls the whole byte, not DQ7-masked, so a "stuck complement" read is the tell.
5. **Per standing bench discipline:** `controller:` identity for the port, live R1/R2 readback, board+shield (Leonardo + Rev 2.0), timestamp — recorded in the EVIDENCE record (mirrors v1.15 `EVIDENCE.{md,json}` schema and Phase 44 `evidence/44-RCA-FINDINGS.md`).

---

## Differential Method (RCA-02)

### Datasheet-grounded axis comparison (both PDFs extracted from `datasheets/0x05-FLASH-AMD-STD/`)

| Axis | W29C040 (FAILS) | W29C020 (PASSES) | Same or Differs? | RCA weight |
|------|-----------------|-------------------|------------------|------------|
| Protocol / handler | `0x05` flash4, `configure_flash4` | `0x05` flash4, `configure_flash4` | **SAME** | Exonerates the dispatch + handler *structure* (the control passes through the identical code) |
| Pinout | `DIP32_SST39SF040` | `DIP32_SST39SF040` | **SAME** [VERIFIED: chip_database.json L14464–14473 / L14444–14453] | Exonerates pinout/pin-1 VPP-vs-A18 confusion as the differential — both use the 5V-flash layout (A18 at pin 1, WE at pin 31) |
| SDP unlock sequence | `5555H←AA, 2AAA←55, 5555←A0` [CITED: W29C040.pdf §7.2 Command Codes for SDP] | `5555H←AA, 2AAA←55, 5555←A0` [CITED: W29C020.pdf §Command Codes for SDP] | **SAME** | SDP addresses/data are identical → SDP content is NOT the differential. (The firmware `FLASH_ENABLE_WRITE` matches both.) |
| Page size | **256 B** (A8–A18 = page addr; A0–A7 = byte-in-page) [CITED: W29C040.pdf §6.2] | **128 B** (A7–A17 = page addr; A0–A6 = byte-in-page) [CITED: W29C020.pdf §6.2] | **DIFFERS** | firmware derives 256/128 correctly via `flash4_page_size(mem_size)` (524288→256, 262144→128) [VERIFIED: flash_type_4.cpp:38]. Page *value* is correct for both → page-size-value is NOT the cause. BUT the *number of bytes loaded per page* differs (256 vs 128) → longer page-load window for W29C040 (H1). |
| Byte-load window T_BLC | **200 µs max** [CITED: W29C040.pdf §6.2 + AC table "Byte Load Cycle Time TBLC – – 200 µS"] | **150 µs** in AC table / 200 µs in §6.2 prose [CITED: W29C020.pdf AC table] | ~SAME spec, but W29C040 loads **2× more bytes per page** within the window | **H1 hinge**: W29C040 must keep the inter-byte gap < 200 µs across **256** consecutive loads; W29C020 across only **128**. Any single inter-byte stall > 200 µs commits the page early → partial/failed page. |
| Address span / lines | 19 lines, **A0–A18** (512 KB) | 18 lines, **A0–A17** (256 KB) | **DIFFERS — A18 is the one extra line** | **H2 hinge**: A18 is the *only* address line W29C040 uses that W29C020 cannot. On Rev 2.0, A18 = `CTRL_ADDRESS_LINE_18_REV2 == CTRL_VPP_P1_ENABLE_REV2 == 0x08` [VERIFIED: rurp_pinout.h:127]. NOTE: page-0 fault is at `0x0000ff` where **A18=0**, so A18-high corruption alone can't explain page-0 — but A18-line *routing/contention* (it shares the P1 bit) could affect the CONTROL-register state during the page load even when nominally 0. |
| Internal write time | 5 ms typ (10 ms wait recommended) [CITED: W29C040.pdf §6.2] | ~10 ms page cycle [CITED: W29C020.pdf features] | ~SAME | poll cap = 1024 × (10 µs + read) ≈ well over 10 ms → poll window is adequate IF the page actually committed. Exonerates "poll too short" unless the read itself is slow. |
| VPP requirement | None — 5V single-supply, internal VPP gen [CITED: W29C040.pdf GENERAL DESCRIPTION] | None — 5V single-supply, internal VPP gen [CITED: W29C020.pdf GENERAL DESCRIPTION] | **SAME** | Both 5V; `vpp_mv=12000` in DB is the chip-ID-read WP/VPP datum, NOT a programming VPP. flash4 write path must set NO VPP bits (verified — see Safety). |

### Firmware branch points where capacity / address width matters
[All VERIFIED by direct source read]
- `flash4_page_size(mem_size)` (flash_type_4.cpp:38) — the ONLY capacity branch; returns 256 for ≥262145, 128 for ≤262144, 64 for ≤65536. **W29C040 → 256 (correct), W29C020 → 128 (correct).** This exonerates page-size *derivation* as the differential.
- `mem_util_calculate_top_address_register` (memory.cpp:187) — packs `(address>>16) & (A16|A17|A18|RW)` into the CONTROL register and OR-preserves VPP/mask bits. **`if (handle->pins < 32)` preserves `CTRL_VPP_VPE_DROP_ENABLE` (==A16 on legacy)** — but BOTH chips are `pin_count==32`, so this branch is NOT taken for either. **The `pins==28` A17-force branch is also not taken.** → top-address packing is identical for both 32-pin chips. Re-examine whether A18 (bit 0x08 on Rev2 = P1) is correctly emitted vs masked.
- `mem_util_remap_address_bus` (memory.cpp:381) — applies the bus-config line remap + `static_high_mask`. Differs only via each chip's `bus_config` (19 vs 18 address lines). The 19th line (A18) is present in W29C040's config, absent in W29C020's.
- **SDP unlock path** `fu_flash_fast_address` (flash_utils.cpp:84) — writes ONLY `LEAST_SIGNIFICANT_BYTE` + `MOST_SIGNIFICANT_BYTE` registers; it does **NOT** write the CONTROL/top-address register. So during the SDP 3-byte sequence, A16–A18 hold **whatever the previous CONTROL write left** (the `flash_util_byte_flipping` prologue does `set_control_register(CTRL_READ_WRITE, 0)`, which clears the RW bit but otherwise read-modify-writes the existing CONTROL state). **This is the subtle H2/H3 hinge** — the SDP addresses 0x5555/0x2AAA are all < 0x10000 (A0–A14), so A16–A18 *should* be 0 for them; but if the CONTROL register retains a stale top-address from a prior byte, the SDP unlock could land on the wrong page's 0x5555. For page 0 this is benign, which is *evidence against* SDP-addressing being the page-0 cause — record this as a partial exoneration.

### The differential, distilled
After holding protocol/handler/pinout/SDP-content/VPP constant (all SAME), only **three** things differ between the failing W29C040 and the passing W29C020:
1. **256 bytes loaded per page vs 128** → 2× longer page-load window → **timing (H1)**.
2. **A18 exists (512 KB) vs not** → one extra address line, sharing the Rev-2 P1 control bit → **addressing (H2)**.
3. **A8 is a page-address bit on W29C040 but a byte-in-page bit on W29C020** (256 vs 128 B page) → the chip's internal page-latch boundary sits at a different address bit. If the firmware's per-byte address emission has any glitch at the A8 boundary specifically for 256 B pages, it manifests on W29C040 only → **firmware-algorithm / addressing (H4/H2)**.

---

## Root-Cause Classification (RCA-03)

Five ranked hypotheses. Each carries a **classification** and a **disconfirming test** (the observation that would *kill* it). Run cheapest-first. A cause is *named* only when it survives its disconfirming test while competitors fail theirs (Phase 44 D-07 bar).

### H1 — Byte-load timing window (T_BLC=200µs) violation mid-page  ★ strongest single hypothesis
**Classification:** TIMING
**Mechanism:** The firmware loads 256 bytes into the page buffer via 256 sequential `memory_set_data` calls. Each call writes LSB + MSB + CONTROL (top-address) registers, then `delayMicroseconds(3)` + CE pulse + `delayMicroseconds(pulse_delay)`. If any inter-byte gap exceeds **200 µs**, the W29C040 terminates the page-load cycle early and starts its internal write with a *partial* page; the subsequent bytes land in a *new* page-load cycle, and the DQ7 poll at byte 255 sees a page that is mid-write or never-completed → `observed=0x00`, timeout. W29C020 (128 B page) loads half as many bytes, so a marginal cadence that just exceeds 200 µs occasionally would bite W29C040 first/worse. Public failure mode for exactly these AMD/JEDEC page parts is "programmer loads the page too slowly" [CITED: TommyPROM 28C notes; Bread80 SDP analysis — Atmel-family parts refuse/commit when T_BLC exceeded].
**Predicts:** a knob that controls per-byte cadence (e.g., `pulse-delay`) moves the failure; a **single-byte write to page 0** (1 byte, no inter-byte gap) SUCCEEDS; a slower host→fw cadence makes it WORSE.
**Disconfirming test:** `firestarter dev read`/write a **single byte to page 0** (`-a 0 -s 1`) and poll — if that single byte programs and verifies cleanly, the per-byte *mechanics* are sound and the fault is the *multi-byte page-load timing* (H1 confirmed). If a single byte *also* fails, H1 is **disconfirmed** (the fault isn't load-window timing). Also: measure the per-byte cadence from the `DEBUG_ADDRESS` trace timestamps / scope; if every inter-byte gap is comfortably < 200 µs, H1 weakens.
**Why ranked #1:** it is the one axis that scales with the 256-vs-128 byte differential AND matches the documented real-world failure mode for these parts AND is consistent with `observed=0x00` (mid-write complement read).

### H2 — A18 / top-address register corruption during the 256 B page load
**Classification:** ADDRESSING
**Mechanism:** A18 on Rev 2.0 is `CTRL_VPP_P1_ENABLE_REV2 (0x08)` — it shares the CONTROL register with VPP-routing bits. During a 256 B page load that crosses the A8 page-internal boundary, every `memory_set_data` rewrites the full CONTROL register via `mem_util_calculate_top_address_register`, which OR-preserves a mask including `CTRL_VPP_P1_ENABLE`. If the top-address calc mishandles A18 (e.g., masks it, or the P1/A18 bit-share causes the page address presented to the chip to wander), the chip sees inconsistent page addresses across the 256 loads → "all bytes must have the same page address" (datasheet §6.2) is violated → page never commits.
**Predicts:** the fault depends on which control bits are set; writing a page where **A18=1** (address `0x40000`) behaves *differently* from page 0 (A18=0); the `DEBUG_ADDRESS` `DBG_TOP_MSB_LSB` trace shows a *changing* top byte across a single 256 B page load (it should be constant within a page).
**Disconfirming test:** capture the `DBG_TOP_MSB_LSB` trace across one full page-0 load. If the top-address byte is **constant** (and correct = 0x00 for page 0) across all 256 bytes, the page address is stable → **H2 disconfirmed for page 0**. (Strongly expected to disconfirm for page 0 specifically, since A18=0 there — but the trace is needed to be sure, and it also informs whether later pages would fail.)
**Note:** because the page-0 fault is at A18=0, H2 is *a priori* weaker for explaining page-0 specifically; keep it as the differential-completeness axis (RCA-02 requires exonerating it explicitly).

### H3 — SDP unlock not actually disabling protection on W29C040 silicon (per-page re-arm / timing)
**Classification:** FIRMWARE-ALGORITHM (sequence) or SILICON (SDP variant)
**Mechanism:** The firmware sends `FLASH_ENABLE_WRITE` (the 3-byte page-load command `AA→5555, 55→2AAA, A0→5555`) once at page start, then loads page bytes. This is the **per-page SDP'd page-load command**, correct per datasheet. BUT: (a) `fu_flash_fast_address` doesn't set the top-address register for the SDP writes — fine for page 0; (b) if the chip shipped with SDP enabled and the 3-byte command must complete within its own timing relative to the first data byte, a slow gap between the A0→5555 command and the first page byte could drop the chip out of the page-load command state. W29C040 SDP could be stricter than W29C020.
**Predicts:** disabling SDP first (the 6-byte SDP-disable flow `AA→5555,55→2AAA,80→5555,AA→5555,55→2AAA,20→5555` = `FLASH_DISABLE_WRITE_PROTECTION` in flash_utils.h) then doing an unprotected page write changes the outcome.
**Disconfirming test:** the native recording-stub already asserts the SDP MSB signature fires per page (`test_flash4_write_execute_emits_sdp`). On silicon: if a single-byte write (H1 test) that *also* sends SDP succeeds, SDP content is fine (H3 disconfirmed). If even the documented SDP page-load command fails for a full page but a single byte works → points back to H1 (timing within the page), not H3.
**Caveat:** H3 and H1 are entangled — both can present as "page didn't commit." The single-byte-vs-full-page fork separates them: single-byte still uses SDP, so single-byte SUCCESS exonerates SDP-content (H3) and indicts page-load timing (H1).

### H4 — Poll/verify site or page-commit-not-triggered (firmware-algorithm)
**Classification:** FIRMWARE-ALGORITHM
**Mechanism:** `flash4_write_execute` triggers the internal write implicitly by *stopping* the byte loads (datasheet: "page load cycle terminated… internal write starts if no additional byte is loaded"). The poll (`flash4_wait_for_page_write` → `poll_readback`) then reads the **last address** and compares the **whole byte** (NOT DQ7-masked, unlike flash3's `flash_util_verify_operation`). During the internal write, the datasheet says reading the last-loaded address returns the **complement of DQ7** until done — so a whole-byte compare can mismatch transiently, but `poll_readback` loops 1024× so it should outlast the 5 ms write. HOWEVER: if the page never committed (H1/H3), the poll reads stale `0x00` forever → timeout. Also: `poll_readback` does `delayMicroseconds(10)` then reads via `memory_get_data` which applies the read-strobe path — if the read itself is mis-timed, the poll could mis-read.
**Predicts:** the poll *result* (`observed`) is the discriminator. `observed=0x00` with a never-erased page = page never committed (→ H1/H3). `observed=0xFF` = erased but not programmed. `observed=0x57` (0xd7 with DQ7 cleared = complement) = mid-write, poll gave up too early.
**Disconfirming test:** after the timeout, immediately `dev read 0x0000ff` several times: if it eventually settles to `0xd7` (the chip *did* finish, poll just gave up) → poll-timing bug (H4 confirmed, fix = poll longer / DQ7-mask). If it stays `0x00`/`0xFF` indefinitely → page truly never programmed (H4 disconfirmed; → H1/H3). The recorded `observed=0x00` already hints the page never committed (favoring H1/H3 over H4), but the post-fail settled read is the clean disconfirmer.

### H5 — Silicon defect / wear on the specific seated W29C040
**Classification:** SILICON
**Mechanism:** The seated part could be a genuinely worn/defective die (cf. the W27E512/W27E040 stuck-bit findings, D-32). The chip-ID reads correctly (`0xda46`) and reads are clean, so it's not dead — but page-0 specifically could be a bad block (the W29C040 has boot-block architecture per datasheet §6.6).
**Predicts:** the fault is **chip-instance-specific** and **page-specific** (page 0 = boot block).
**Disconfirming test:** (a) write a **non-page-0** page (e.g., `-a 0x1000`) — if a middle page programs cleanly but page 0 never does, suspect the boot block / page-0 specificity (could be silicon OR an addressing bug at the A8 boundary). (b) If a *second* W29C040 part is available, repeat — instance-specificity = silicon. (c) Since W29C020 (different die) passes and W29C040 fails deterministically across reseats, pure random silicon failure is *already* weakened; H5 is the residual "named disconfirmed hypothesis" to record if H1–H4 all survive their disconfirming tests (i.e., the code is exonerated and the chip is the variable). Note the W29C040 boot-block lockout (§6.6) is a real datasheet feature worth checking against page 0.

### Recommended disconfirming-test execution order (cheapest-first)
1. **Post-fail settled read of `0x0000ff`** (H4 fork; free — just read after the recorded fail). Decides "page committed but poll gave up" vs "page never committed."
2. **Single byte to page 0** (`write -a 0 -s 1`) (H1/H3 fork). Decides "per-byte mechanics OK, multi-byte timing bad" vs "even one byte fails."
3. **`DEBUG_ADDRESS` trace of one page-0 load** (H2 + H1 cadence). Decides A18/top-address stability + per-byte timing.
4. **Non-page-0 page write** (`write -a 0x1000`) (H5 / page-0-specificity).
5. **A18=1 page write** (`write -a 0x40000`) (H2 completeness — exonerate/indict A18).

### Expected verdict shape (for the planner)
Based on the recorded `observed=0x00` + the 256-vs-128 byte differential + the documented real-world failure mode, the **leading candidate is H1 (timing — byte-load window mid-page)**, with H4 (poll site) as the most likely *contributing* firmware-algorithm factor (whole-byte vs DQ7-masked poll). The RCA must still run the disconfirming matrix; the planner should size the phase for **all five** disconfirming tests (they are cheap, mostly bench reads/writes) and a written `evidence/93-RCA-FINDINGS.md` naming the survivor.

---

## Runtime State Inventory

> This is a diagnostic phase (no rename/refactor/migration), but it DOES sideload firmware and seat silicon, so the inventory is filled for completeness.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | The seated **W29C040 silicon** holds whatever the failed write left (page 0 = `0x00` per recorded signature). Repro write attempts mutate the chip's contents. | None — the chip is the device under test; record pre/post state in EVIDENCE. No data migration. |
| Live service config | **Firmware build flag `DEBUG_ADDRESS`** is a build-time toggle, not committed-enabled (commented in `platformio.ini:25`). An RCA trace build sets it transiently. | If a `DEBUG_ADDRESS` build is flashed for tracing, **re-flash the normal build** after RCA (or note the trace build is RCA-only and never committed). Leonardo is chip-OUT-sideload-EXEMPT — do NOT instruct chip removal before sideload. |
| OS-registered state | None — no host services/schedulers involved. | None — verified: RCA is CLI-driven over serial. |
| Secrets/env vars | `FIRESTARTER_CONFIG_DIR` test seam (used in v1.15) may point the host at a saved config/port. | Confirm the host is using the real seated-board config, not a stale saved port (the v1.14 "live board + saved config port" false-fail lesson). Verify `controller:` identity per task. |
| Build artifacts | A transient `DEBUG_ADDRESS` firmware `.hex`; the editable host install. | None persistent — re-flash normal firmware post-RCA; no `egg-info`/package rename. |

**Nothing found in category:** OS-registered state — None (verified: RCA is serial-CLI only, no scheduler/service registration).

---

## Common Pitfalls

### Pitfall 1: Concluding "missing SDP" or "wrong page size" (the Phase-74 trap)
**What goes wrong:** Re-naming the already-applied Phase-74 fixes as the cause.
**Why it happens:** They are the textbook causes for AMD/JEDEC page-write failures, and the Phase-74 research named them — but they're already in the code on `a296195` and proven silicon-ineffective.
**How to avoid:** The RCA's first sanity check is `pio test -e native -f "*test_val_flash4*"` (confirms SDP is emitted + page size is 256) AND reading flash_type_4.cpp:38/104 (confirms both present). Then move past them.
**Warning signs:** any finding that recommends "add SDP" / "set page size 256" — both already done.

### Pitfall 2: `write -b` skipped-erase artifact
**What goes wrong:** A pre-HARD-01 host build's `-b` skips erase, so a non-blank chip "fails" for the wrong reason.
**Why it happens:** Historical `-b` ⇒ `FLAG_SKIP_ERASE` coupling (v1.16 P90/91 "regression" was exactly this test-method error).
**How to avoid:** Use a post-HARD-01 host build; verify pre-write erase runs for the Flash/EEPROM W29C040; confirm via `firestarter --version` / changelog. The W29C040 auto-erases per-page anyway, but rule the artifact out.
**Warning signs:** the chip "fails" only with `-b` but a plain `write` differs.

### Pitfall 3: `flash4_erase_execute` asserts VPP regulator bits (latent SAFE-01 concern)
**What goes wrong:** `flash4_erase_execute` (flash_type_4.cpp:148–180) asserts `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE | CTRL_VPE_ENABLE` (12V boost) — wrong for a 5V-only W29C040.
**Why it happens:** legacy erase code; flagged in Phase-74 research as latent because no flash4 DB chip sets `FLAG_CAN_ERASE` (host only sets it for the 0x07 EE-EPROM path) → the erase branch is dead code for flash4.
**How to avoid:** Confirm `FLAG_CAN_ERASE` is NOT set in the W29C040 wire command (inspect the JSON cmd / `flags` field). If it IS set, the VPP-asserting erase fires → both a SAFE-01 concern AND a possible confounder (12V on a 5V chip). The flash4 *write_execute* path (the one under test) provably sets **no** VPP bits (verified — see Safety), but the *erase* path called from `write_init` must be checked. **This is a key SAFE-01 verification for RCA-01.**
**Warning signs:** the wire `flags` field includes `FLAG_CAN_ERASE (0x02)` for W29C040; any VPP control bit in a `DEBUG_ADDRESS`/`dev` trace during the write cycle.

### Pitfall 4: N=1 bench conclusions / port-identity drift
**What goes wrong:** Naming a cause from a single run, or running against the wrong port after a reseat.
**Why it happens:** /dev/ttyACM* numbers shuffle on replug (memory: `feedback_verify_port_identity_each_task`).
**How to avoid:** N≥2 deterministic repro; verify `controller:` identity + live R1/R2 readback at every bench task.
**Warning signs:** R1 outside 270000 ± 25%; controller identity mismatch.

### Pitfall 5: `delayMicroseconds` accuracy < 3 µs on 16 MHz AVR
**What goes wrong:** Sub-3-µs delays are inaccurate on the Leonardo, so per-byte timing measured from code constants may not match silicon.
**Why it happens:** AVR `delayMicroseconds` resolution (noted in memory.cpp:313).
**How to avoid:** For H1, measure per-byte cadence empirically (scope or `DEBUG_ADDRESS` trace timestamps), not by summing code-constant delays.
**Warning signs:** computed per-byte time near the 200 µs boundary — measure, don't assume.

---

## Code Examples

Verified in-repo patterns the RCA leans on (all [VERIFIED: direct source read]):

### The failing page-load loop (the code under investigation)
```cpp
// Source: firestarter/src/proms/flash_type_4.cpp:91 (a296195 recompose)
void flash4_write_execute(firestarter_handle_t* handle) {
    uint32_t page_size = flash4_page_size(handle->mem_size);   // W29C040: 256
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint32_t address = handle->address + i;
        uint8_t expected = handle->data_buffer[i];
        bool is_page_start = (address % page_size) == 0;
        bool is_first_byte = (i == 0);
        if (is_page_start || is_first_byte) {
            flash_execute_command(FLASH_ENABLE_WRITE);          // SDP page-load cmd, per page
        }
        handle->firestarter_set_data(handle, address, expected); // full LSB+MSB+CONTROL each byte
        bool reached_page_end = ((address + 1) % page_size) == 0;
        bool is_last_byte = i == handle->data_size - 1;
        if (reached_page_end || is_last_byte) {
            if (!flash4_wait_for_page_write(handle, address, expected)) return;  // poll @ last byte
        }
    }
}
```

### The poll that times out (whole-byte compare, NOT DQ7-masked — H4 clue)
```cpp
// Source: firestarter/src/proms/primitives.cpp:70 (P5 primitive, cap=1024 from flash4)
bool poll_readback(firestarter_handle_t* handle, uint32_t address, uint8_t expected,
                   uint16_t max_iters, uint8_t* observed_out) {
    uint8_t observed = 0;
    for (uint16_t j = 0; j < max_iters; j++) {
        delayMicroseconds(10);
        observed = handle->firestarter_get_data(handle, address);
        if (observed == expected) return true;     // FULL byte, not (observed & 0x80)==(expected & 0x80)
    }
    if (observed_out) *observed_out = observed;     // recorded 0x00 → page never committed (H1/H3) OR mid-write complement
    return false;
}
```
> Contrast flash3's `flash_util_verify_operation` (flash_utils.cpp:52) which DOES DQ7-mask (`(poll & 0x80) == (expected & 0x80)`) and double-reads. flash4's whole-byte poll is a deliberate divergence — note it for H4.

### Per-byte address emission (sets full top-address every byte — relevant to H1 cost + H2 stability)
```cpp
// Source: firestarter/src/proms/memory.cpp:204 + :274
void memory_set_data(firestarter_handle_t* handle, uint32_t address, uint8_t data) {
    rurp_chip_input();
    address = mem_util_remap_address_bus(handle, address, WRITE_FLAG);
    handle->firestarter_set_address(handle, address);   // writes LSB, MSB, AND CONTROL(top A16-A18)
    rurp_write_data_buffer(data);
    delayMicroseconds(3);
    rurp_chip_enable();
    delayMicroseconds(handle->pulse_delay);             // flash4 pulse_delay = "Algorithm Controlled" → check resolved value
    rurp_chip_disable();
}
```

### The passive trace build flag (SAFE-01-safe instrumentation)
```ini
# Source: firestarter/platformio.ini:25  (commented; enable for an RCA trace build)
# -D DEBUG_ADDRESS    ; emits DBG_ADDRESS (U24) + DBG_TOP_MSB_LSB per mem_util_set_address
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Phase-74 hypothesis: "flash4 fails because SDP missing + page size 64" | Both fixed + present on `a296195`, yet silicon still FAILS deterministically | v1.15 Phase 82/84 | RCA must go deeper than SDP/page-size |
| flash4 had its own SDP/poll/chip-id code | Recomposed onto P7/P4/P3/P5 shared primitives (poll = `poll_readback`) | v1.16 Phase 89 | The poll site is now the shared P5 primitive; behavior preserved (golden traces) |
| "No W29C040 datasheet committed" (STATE.md:90) | **Both W29C040 + W29C020 datasheets present** in `datasheets/0x05-FLASH-AMD-STD/` | v1.16 datasheet acquisition | No datasheet acquisition needed in Phase 93 (STATE.md note is stale) |
| `-b` ⇒ skip erase | `-b` decoupled from skip-erase; explicit `--skip-erase` opt-in | v1.16 Phase 92 (HARD-01) | The "12V-VPP regression" was a test-method artifact; ensure repro uses a post-HARD-01 host |

**Deprecated/outdated:**
- STATE.md line 90 "no W29C040 datasheet committed yet" — outdated; both PDFs are in-repo.
- The standalone `flash4_erase_execute` 12V-VPP erase — latent dead code (no flash4 DB chip sets `FLAG_CAN_ERASE`); verify, don't trust.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The seated W29C040 is the same physical part class that failed in v1.15 (chip-id `0xda46`), not a different revision/manufacturer | Reproduction | If a different part, the page architecture (boot block, page size) could differ; verify `firestarter info`/chip-id at the bench |
| A2 | The current host build is post-HARD-01 (so `-b` does NOT skip erase) | Pitfall 2 | A pre-HARD-01 host would produce a skipped-erase artifact mistaken for the page-write fault; confirm host version |
| A3 | flash4 `pulse_delay` resolves to a small value (per-byte cost stays << 200 µs nominal) — "Algorithm Controlled" in DB | H1, Code Examples | If `pulse_delay` resolves large, the per-byte cost is bigger and H1 is more likely; the planner should have the bench print the resolved `pulse-delay` in the wire cmd |
| A4 | `FLAG_CAN_ERASE` is NOT set for W29C040 (so the VPP-asserting `flash4_erase_execute` is not invoked) | Pitfall 3, Safety | If set, a 12V erase fires on a 5V chip — SAFE-01 concern AND a confounder; inspect the wire `flags` field |
| A5 | W29C040 SDP unlock content equals W29C020's (both `AA→5555,55→2AAA,A0→5555`) — confirmed in both datasheets | Differential | Verified by datasheet extraction; low risk |
| A6 | The recorded `observed=0x00` reflects "page never committed" rather than a mid-write DQ7-complement that the poll outlasted | RCA-03 H4 | The post-fail settled-read disconfirming test resolves this directly; until run, H1-vs-H4 weighting is provisional |
| A7 | A18 routing on Rev 2.0 (`CTRL_ADDRESS_LINE_18_REV2 == CTRL_VPP_P1_ENABLE_REV2 == 0x08`) is the active layout for the seated shield | Differential H2 | If the shield is actually a different rev, the control-bit map differs; always ASK which silkscreen rev (memory: `user_shield_revisions`) — but milestone locks Rev 2.0 |

**If this table is empty:** it is not — A1–A7 are assumptions the discuss-phase / bench should confirm before the named cause is locked.

---

## Open Questions

1. **Does a single byte to page 0 program cleanly?**
   - What we know: a full 256 B page-0 load times out at byte 255 with `observed=0x00`.
   - What's unclear: whether 1 byte (no inter-byte gap) succeeds.
   - Recommendation: run disconfirming test #2 first-thing — it forks H1/H3 (timing/SDP) from H4/H5 (poll/silicon) in one shot.

2. **Did the page commit but the poll give up (H4), or never commit (H1/H3)?**
   - What we know: poll read `0x00`.
   - What's unclear: the *settled* value after the timeout.
   - Recommendation: disconfirming test #1 (free) — read `0x0000ff` repeatedly post-fail.

3. **What does the per-byte cadence actually measure on silicon (vs the 200 µs T_BLC)?**
   - What we know: the per-byte path writes 3 registers + 2 delays + a CE pulse; `delayMicroseconds<3µs` is inaccurate on 16 MHz AVR.
   - What's unclear: empirical inter-byte µs.
   - Recommendation: `DEBUG_ADDRESS` trace timestamps or operator scope; needed to confirm/deny H1 quantitatively.

4. **Is `FLAG_CAN_ERASE` set for W29C040, invoking the 12V-asserting `flash4_erase_execute`?**
   - What we know: Phase-74 research says no flash4 DB chip sets it; the erase asserts VPP bits.
   - What's unclear: the actual wire `flags` for *this* chip on *this* host build.
   - Recommendation: inspect the JSON wire command (host debug) — also a SAFE-01 verification.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Leonardo board + RURP Rev 2.0 + seated W29C040 | All bench repro / differential / disconfirming tests | operator-provided (locked) | Rev 2.0 | none — phase is hardware-gated; operator seats the chip |
| W29C020 (differential control) | RCA-02 differential | operator inventory (passed v1.15) | — | If unavailable, lean harder on datasheet differential + native tests; but bench control is strongly preferred |
| `firestarter` host CLI (editable) | Drive repro + `dev` instrumentation | ✓ (`pip install -e .`) | post-HARD-01 expected | restore via `pip install -e '.[test]'` (memory: devcontainer python env) |
| `pio` (PlatformIO) | Build `leonardo` + optional `DEBUG_ADDRESS` trace build; `pio test -e native` | ✓ | in-repo | none |
| W29C040.pdf / W29C020.pdf | Datasheet differential | ✓ in-repo | Rev A11 / A3 | n/a (present) |
| `pypdf` | Datasheet text extraction | ✓ container python | — | `pdftotext` (poppler) is ABSENT — use `pypdf` |
| Logic analyzer / oscilloscope | H1 sub-µs timing ground-truth (optional) | operator-only | — | `DEBUG_ADDRESS` serial trace timestamps (coarser but unattended) |

**Missing dependencies with no fallback:** the bench hardware (Leonardo + Rev 2.0 + seated W29C040) — inherent to a hardware-gated RCA; operator-provided per milestone lock.
**Missing dependencies with fallback:** `poppler` (use `pypdf`); scope (use `DEBUG_ADDRESS` trace); W29C020 control (lean on datasheet + native if absent, but bench control strongly preferred).

---

## Validation Architecture

> For an RCA phase there is **no production code to test** — the "validation" is that the named
> root cause is *correct and sufficient*. The Nyquist frame here = the disconfirming-test matrix:
> each hypothesis carries an automated/observable check that would sample (confirm or refute) it.
> `workflow.nyquist_validation` is absent in config.json → treated as enabled.

### Test Framework
| Property | Value |
|----------|-------|
| Native (sequence) framework | Unity via `pio test -e native` (`[env:native]`, recording-bus stub) |
| Native config | `firestarter/platformio.ini` `[env:native]` (`src_filter=+<proms/>`, `test_build_src=yes`) |
| Quick native run | `pio test -e native -f "*test_val_flash4*"` |
| Full native suite | `pio test -e native` |
| Bench (silicon) "framework" | `firestarter dev write-cycle` (0/1/2 verdict) + `firestarter dev read` + `DEBUG_ADDRESS` trace build |

### RCA Requirements → Evidence Map (the disconfirming-test matrix is the "test map")
| Req ID | Behavior to validate | Evidence Type | Command / Observation | Exists? |
|--------|----------------------|---------------|------------------------|---------|
| RCA-01 | Fault reproduces with captured signature | bench (silicon) | `firestarter write -b W29C040 <img>` → record ERROR frame; `dev write-cycle … --runs 2` (N≥2) | ✅ commands exist |
| RCA-01 | DQ7/whole-byte poll behavior at failing addr | bench | post-fail `dev read W29C040 -a 0xff -s 1` ×N (settled value) | ✅ |
| RCA-01 | SDP emitted + page size correct (rule out Phase-74 trap) | native | `pio test -e native -f "*test_val_flash4*"` | ✅ `test_flash4_write_execute_emits_sdp` + INV-04 page-boundary test |
| RCA-02 | W29C020 control passes same code path | bench | `firestarter write -b W29C020 <128K img>` → PASS | ✅ (passed v1.15) |
| RCA-02 | A18 / top-address stable within a page (H2) | bench trace | `DEBUG_ADDRESS` build → inspect `DBG_TOP_MSB_LSB` across page-0 load | ✅ build flag exists |
| RCA-03 H1 | single byte to page 0 succeeds (timing fork) | bench | `firestarter write W29C040 -a 0 -s 1` + verify | ✅ |
| RCA-03 H4 | settled read distinguishes "committed-but-poll-gave-up" vs "never committed" | bench | repeated `dev read 0xff` post-fail | ✅ |
| RCA-03 H5 | page-0-specific vs general (boot block / silicon) | bench | `firestarter write W29C040 -a 0x1000 …` middle page | ✅ |
| SAFE-01 | flash4 write path sets NO VPP bits; `FLAG_CAN_ERASE` not set | native + wire inspect | `test_flash4_write_execute_no_vpp` (native, green) + inspect wire `flags` | ✅ native test exists |

### Sampling Rate
- **Per RCA experiment:** record the ERROR frame + verdict + (where relevant) the trace/settled-read into `evidence/`.
- **Before naming a cause:** all five disconfirming tests run; the survivor cited with its silicon evidence.
- **Phase gate (→ Phase 94):** `evidence/93-RCA-FINDINGS.md` exists naming the root cause (or ranked disconfirmed hypotheses), classified, with the disconfirming evidence — sufficient that Phase 94 designs a fix with no further RCA.

### Wave 0 Gaps
- [ ] `evidence/93-RCA-FINDINGS.md` — canonical named root cause (mirror `evidence/44-RCA-FINDINGS.md` structure from Phase 44).
- [ ] `evidence/` capture dirs (signature/, differential/) — created at first bench task.
- [ ] (Optional) a `DEBUG_ADDRESS` trace firmware build — RCA-only, re-flash normal build after.
- No new automated test files are *required* — the native flash4 suite already exists; bench evidence is recorded, not unit-tested. (If H4 names a poll-site bug, the *Phase 94 fix* adds the regression test, not Phase 93.)

*Existing native infrastructure (`test_val_flash4`, `test_configure_memory`) covers the sequence-level checks Phase 93 needs; the silicon-level checks are bench observations, not automatable in CI.*

---

## Security Domain

> `security_enforcement` is absent in config.json → treated as enabled. This is firmware/hardware RCA;
> the relevant "security" surface is **hardware-safety + the SAFE-01 non-bypass guard**, not web ASVS.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | local CLI to local serial device; no auth surface |
| V3 Session Management | no | n/a |
| V4 Access Control | no | n/a |
| V5 Input Validation | yes (firmware-side) | host `chip_resolver.resolve_chip` validates the chip before any serial byte (in-host refusal); firmware `eeprom28c` underflow guard / VPP window check validate hardware-unsafe ops. RCA must NOT bypass these. |
| V6 Cryptography | no | (transport CRC8/COBS is integrity, already settled v1.10) |

### Known Threat Patterns for this stack (hardware-safety framing)
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| 12V VPP boost asserted on a 5V-only W29C040 (over-voltage / chip damage) | Tampering / DoS (hardware) | firmware VPP window check stays armed; flash4 *write* path provably sets no VPP bits [VERIFIED: `test_flash4_write_execute_no_vpp` green]; verify `FLAG_CAN_ERASE` is NOT set so the 12V-asserting `flash4_erase_execute` never fires (Pitfall 3) |
| Test-only escape hatch bypassing dispatch to "force" the write | Elevation of Privilege (bypassing safety dispatch) | SAFE-01: forbidden. All RCA flows through normal `0x05` dispatch + existing `dev` commands; `DEBUG_ADDRESS` is a passive trace, not a dispatch bypass |
| Bypassing `chip_resolver.resolve_chip` host guard | Spoofing the supported-status gate | SAFE-01: never bypass; the W29C040 is already `supported` in the DB so it resolves normally |
| Over-voltage on A9 during chip-ID read (12.5V max per datasheet) | Tampering (hardware) | chip-ID read uses the existing A9-12V path (unchanged); RCA does not modify it |

**SAFE-01 verification checklist for the planner:**
- [ ] Confirm `test_flash4_write_execute_no_vpp` is green on `a296195` (no VPP bits in write-execute).
- [ ] Inspect the W29C040 wire command `flags` field — confirm `FLAG_CAN_ERASE (0x02)` is absent (else the 12V erase path is live).
- [ ] Confirm any `DEBUG_ADDRESS` trace build still routes W29C040 through `configure_flash4` (no dispatch change).
- [ ] Confirm `chip_resolver.resolve_chip("W29C040")` succeeds normally (no `--force`-style bypass of the supported gate).

---

## Sources

### Primary (HIGH confidence)
- `firestarter/src/proms/flash_type_4.cpp` (a296195) — `flash4_write_execute`, `flash4_wait_for_page_write`, `flash4_page_size` — direct read
- `firestarter/src/proms/primitives.cpp` — `poll_readback` P5 (whole-byte compare) — direct read
- `firestarter/src/proms/flash_utils.cpp` + `include/flash_utils.h` — `FLASH_ENABLE_WRITE` SDP, `fu_flash_fast_address` (LSB/MSB only), DQ7-masked `flash_util_verify_operation` — direct read
- `firestarter/src/proms/memory.cpp` — `memory_set_data`, `mem_util_set_address`, `mem_util_calculate_top_address_register`, `mem_util_remap_address_bus` — direct read
- `firestarter/include/rurp_pinout.h` — Rev-2 control-bit map (`CTRL_ADDRESS_LINE_18_REV2 == CTRL_VPP_P1_ENABLE_REV2 == 0x08`) — direct read
- `datasheets/0x05-FLASH-AMD-STD/W29C040.pdf` (Rev A11) — §6.2 Page Write (A8–A18 page addr, 256 B, T_BLC=200µs), §6.7 DQ7 polling (complement during write), §7.2 SDP command codes, §6.6 boot block — extracted via pypdf
- `datasheets/0x05-FLASH-AMD-STD/W29C020.pdf` (Rev A3) — §6.2 (A7–A17 page addr, 128 B), SDP command codes, AC table T_BLC — extracted via pypdf
- `.planning/v1.15/bench/EVIDENCE.md` Phase 82 + Phase 84 Task 3c — the recorded `Timeout verifying 0xd7 at 0x0000ff (got 0x00)` signature, N=2 deterministic — direct read
- `firestarter_app/firestarter/cli_handlers.py` — `dev write-cycle`/`dev read`/`dev reg`/`dev addr`/`dev consistency-check`/`dev fault-inject` instrumentation surface — direct read
- `firestarter_app/firestarter/data/chip_database.json` (L14444–14473) — W29C040 + W29C020 entries (both `DIP32_SST39SF040`, algo 5, sizes 524288/262144) — direct read
- `firestarter_app/firestarter/data/pinouts.json` — `DIP32_SST39SF040` bus-config (19 address lines, A18 at pin 1, rw at pin 31) — direct read
- `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp` — SDP-emission + INV-04 256B-boundary native asserts; `test_flash4_write_execute_no_vpp` — direct read
- `.planning/phases/74-.../74-RESEARCH.md` — the prior (silicon-ineffective) hypothesis + datasheet analysis — direct read

### Secondary (MEDIUM confidence)
- WebSearch (W29C040 SDP / page-write programmer failures) — corroborates the **T_BLC byte-load-window timing** as the dominant real-world failure mode for AMD/JEDEC page-write parts (TommyPROM 28C notes; Bread80 SDP analysis; Elnec/Winbond device pages).

### Tertiary (LOW confidence)
- General AMD/JEDEC page-write community lore on DQ7-complement-during-write semantics — used only to interpret `observed=0x00`; the datasheet §6.7 is the authoritative version cited above.

## Metadata

**Confidence breakdown:**
- Failure signature / reproduction: HIGH — recorded verbatim, N=2 deterministic, exact command + error frame known
- Differential axes: HIGH — both datasheets extracted in-repo; firmware branch points read directly; only A18 + page-byte-count + (entangled) timing differ
- Root-cause hypotheses: MEDIUM — H1 (timing) is the leading candidate by mechanism + community evidence + `observed=0x00`, but NOT yet bench-confirmed; the disconfirming-test matrix is designed but unrun (that is Phase 93's bench work)
- Safety/instrumentation boundaries: HIGH — flash4 write path verified VPP-free; all instrumentation is in-tree + non-bypassing

**Research date:** 2026-06-26
**Valid until:** 2026-07-26 (stable — firmware on `a296195`; datasheets immutable; the only moving part is the bench evidence the phase itself produces)

## Sources (web)
- [28C EEPROMs and Software Data Protection (SDP) — TommyPROM](https://tomnisbet.github.io/TommyPROM/docs/28C256-notes)
- [The Ben Eater EEPROM Programmer, 28C256 and Software Data Protection — Bread80.com](https://bread80.com/the-ben-eater-eeprom-programmer-28c256-and-software-data-protection/)
- [Programmer for W29C040 — Winbond | Elnec](https://www.elnec.com/en/device/Winbond/W29C040/)
- [W29C040 Datasheet (PDF) — Winbond | AllDataSheet](https://www.alldatasheet.com/datasheet-pdf/pdf/47664/WINBOND/W29C040.html)
