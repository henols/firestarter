# Phase 91: 12V-VPP Write-Path Regression RCA - Research

**Researched:** 2026-06-26
**Domain:** Firmware/host write-path regression RCA (AVR C++ firmware + Python host CLI), code-level diff forensics + bench A/B design
**Confidence:** HIGH (code/diff facts), MEDIUM (mechanism hypothesis pending the bench A/B)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Operator has left the bench and handed full autonomous control.** Do NOT ask questions — keep working until the issues are fixed and the SST39SF040 is confirmed working. Make and record reasonable engineering calls.
- **Controller:** Leonardo on `/dev/ttyACM0` (`firestarter fw` → `leonardo`, version string `3.0.0b10`).
- **Shield:** RURP **Rev 2.0** — operator-stated silkscreen is ground truth; no shield swap this session.
- **Chip seated:** SST39SF040 (0x06). Operator measured all pins → properly seated; do NOT attribute failures to seating.
- **Firmware reflashing authorized** with the SST39SF040 left in the socket — Leonardo is EXEMPT from chip-out-before-sideload. This unblocks the A/B (flash b10 vs a296195).
- **Scope split:** SST39SF040 (0x06) full bench work IS in scope now (reproduce → A/B → fix → confirm write+verify). W27C512 (0x07) bench re-validation is DEFERRED to operator return (chip swap); its RCA analysis + fix design remain in scope now.
- **A/B method:** firmware `a296195` (recompose) vs `a1953c2` (tag `3.0.0b10`, v1.15 baseline). Build `pio run -e leonardo`, flash `pio run -t upload -e leonardo`, confirm `firestarter fw` before each silicon op. Host: `firestarter_app@e46549f` (current v1.16) vs `98b3a92` (v1.15 host). Vary ONE axis at a time.
- **Write-cycle method:** v1.15 `write -b` direct path (`write -b A` → `verify A` → `write -b B` → `verify B` → `consistency-check N=3`). Do NOT use `dev write-cycle` (blank-check fails on flash). PASS = write-cycle-final SHA byte-identical to v1.15 baseline.
- **Submodule gitlinks stay PINNED at b10** (D-06). Fix commits land inside the sub-repo on the v1.16 branch.

### Claude's Discretion
- Mechanism explanation and ranked candidate root causes.
- Exact A/B sequencing and which experiment runs first.
- Engineering disposition of the 0x06/0x07 PROTOCOL-LEDGER rows (within the scope fence).

### Deferred Ideas (OUT OF SCOPE)
- W27C512 0x07 bench PASS + ledger graduation → operator-return bench checklist.
- Any broader recompose audit beyond the 12V-VPP write path → only if the RCA points there.
- No shield swap, no other chips, no gitlink bump, no new programming capability, no beta/stable tag promotion.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| RCA-91 | Attribute the regression via controlled A/B (recompose-causal vs pre-existing; fw vs host) AND explain BOTH symptoms (W27C512 bad-bytes-@0x0 at clean 12.0V; SST39SF040 write-A-timeout + deterministically-wrong write-B). | §Root-Cause Analysis (diff forensics proving zero write-path delta in both fw and host); §A/B Procedure (the decisive reflash-b10 experiment); §Mechanism for Both Symptoms. |
| FIX-91 | Propose + apply a fix (or documented accepted deferral); SST39SF040 (0x06) write+verify bench-confirmed byte-identical to v1.15 baseline; W27C512 (0x07) left as ready-to-run operator checklist; 0x06/0x07 PROTOCOL-LEDGER rows dispositioned. Advances LEDGER-02 for 0x06. | §Fix Decision Tree (branch on A/B outcome); §W27C512 Operator Checklist; §Ledger Disposition. |
</phase_requirements>

## Summary

The Phase-90 bench recorded a reproducible "12V-VPP write-path regression" on recompose firmware `a296195`: SST39SF040 (0x06) and W27C512 (0x07) writes fail while all reads and the two 5V writes (W29C020 0x05, FM1608 0x28) pass and match v1.15 byte-for-byte. The CONTEXT framing assumes this is **recompose-caused** and expects the reflash-b10 A/B to clear the SST39SF040.

A complete code-level forensic pass over the primary RCA artifact (`git diff a1953c2..a296195` in `firestarter`, plus `git diff 98b3a92..e46549f` in `firestarter_app`) produces a result that **contradicts the recompose-causal prior**: there is **no behavioral change on either failing chip's write path** in either repo. (1) `flash_type_3.cpp` (0x06 handler) got a comment header and **zero code change**. (2) `eprom.cpp` (0x07 handler) changed only `eprom_check_vpp` (the VPP *measurement* function) and the chip-id wrapper — both behavior-preserving extractions to `primitives.cpp` whose bodies are byte-identical to the originals; `eprom_write_execute` and the erase pulse are untouched. (3) The shared `poll_readback` primitive (P5) is byte-identical to the old flash4 loop — and flash4 PASSED with it. (4) **Both chips' `chip_database.json` entries are byte-identical between v1.15 and v1.16** (algorithm, vpp_mv, pulse_duration, size, type, FLAG_CAN_ERASE derivation all unchanged). (5) The host `eprom_operations.py` write data path is unchanged for these protocols (only a cosmetic output-dir grouping + a SRAM-only blank-check short-circuit landed).

**Primary recommendation:** Treat the leading hypothesis as **"NOT a recompose regression — the failures are environmental / bench-state / pre-existing, surfaced (not introduced) by the recompose."** The reflash-b10 A/B is the decisive experiment and the planner must NOT assume it will clear the chip; plan for the high-probability outcome that **b10 fw ALSO fails**, which proves the recompose innocent and redirects the fix to the bench/chip-state axis. The single most important sub-finding is documented in project memory: a W27C512 "`bad bytes:N/1024`" failure is a **chip-state/erase-rail symptom, not a transport or firmware fault**, and the SST39SF040 flash3 write is a known ~240s slow-path that a ~177s host timeout window can clip. Both symptoms have non-regression explanations that the A/B will adjudicate.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Diff forensics (what changed in the recompose) | Firmware sub-repo (`firestarter`) | Host sub-repo (`firestarter_app`) | The recompose lives in firmware; the host moved v1.15→v1.16 in parallel and must be ruled in/out too. |
| Write-command construction (algorithm, vpp_mv, pulse, flags) | Host CLI (`database.py` → wire dict) | — | The host builds the JSON command from `chip_database.json`; a DB regen is the only host axis that could change wire params. |
| VPP rail enable/route/settle + write pulse + erase pulse | Firmware handlers (`eprom.cpp`, `flash_type_3.cpp`) | Shield hardware (Rev 2.0 regulator) | 12V routing is firmware-keyed on `handle->protocol`; the physical rail is shield/regulator-owned. |
| Post-write verify / readback poll | Firmware (`poll_readback` P5, `verify_and_update_mask`) | Host (`verify` re-read + SHA) | Firmware polls cells; host re-reads and compares SHA to the image. |
| A/B build + flash | Bench tooling (`pio`) | — | `pio run -e leonardo` / `pio run -t upload -e leonardo`; native Unity via `pio test -e native`. |
| Byte-identity gate (silicon truth) | Bench (Leonardo + Rev 2.0 + real chip) | — | Only real silicon can confirm the write actually programmed; the SHA gate is the oracle. |

## Standard Stack

No new packages. This phase uses the existing toolchain only.

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| PlatformIO Core (`pio`) | 6.1.19 (verified on PATH `/usr/local/bin/pio`) | Build/flash firmware (`-e leonardo`), run native Unity tests (`-e native`) | Project-standard per `firestarter/CLAUDE.md`. |
| avrdude (via `pio run -t upload`) | bundled with PlatformIO leonardo platform | Sideload the Leonardo over `/dev/ttyACM0` | Standard Leonardo upload path. |
| `firestarter` CLI (host, pip `-e`) | `firestarter_app@e46549f` (v1.16) / `98b3a92` (v1.15) | Issue `fw`/`hw`/`write -b`/`verify`/`dev consistency-check` | Project host CLI; the A/B host axis. |
| Unity (PlatformIO `test_framework=unity`, `[env:native]`) | bundled | Host-side firmware tests with NO board | `flash3`/`eprom` golden traces already exist (Phase 88). |
| Python 3 + git | system | Diff `chip_database.json` entries; worktree management for the A/B | Forensic + isolation tooling. |

**Installation:** none. Host dev install if the toolchain was wiped: `pip install -e '.[test]'` from `firestarter_app/` using the `/usr/local` python (per project memory `reference_firestarter_app_python_test_env`).

**Version verification:** `pio --version` → `PlatformIO Core, version 6.1.19` (verified this session). No registry packages added → Package Legitimacy Audit not applicable.

## Package Legitimacy Audit

Not applicable — this phase installs **no external packages**. It builds/flashes existing firmware and runs the existing host CLI + native Unity suites. No npm/PyPI/crates additions.

## Architecture Patterns

### System Architecture Diagram — the write path under investigation

```
firestarter CLI (host)                          Leonardo firmware (a296195 or a1953c2)
─────────────────────                           ──────────────────────────────────────
 write -b <chip> <img>
   │
   ├─ database.py.convert_to_programmer()
   │     reads chip_database.json entry  ──────► algorithm (0x06|0x07), vpp_mv (12000),
   │     builds wire dict                        pulse-delay, size, flags(FLAG_CAN_ERASE)
   │                                              [VERIFIED byte-identical v1.15↔v1.16]
   │
   ├─ serial_comm.py  (COBS+CRC8, 250000 baud)   [UNCHANGED for 0x06/0x07]
   │     JSON command  ──────────────────────►  json_parser → firestarter_handle_t
   │                                                  │
   │                                            memory.cpp configure_memory()
   │                                              dispatch on handle->protocol
   │                                                  │
   │            0x06 ────────────────────────► configure_flash3() [flash_type_3.cpp]
   │                                              5V, NO VPP regulator; AMD/SST unlock
   │                                              3-cycle → byte program → DQ7 poll
   │                                              [DIFF = comment header ONLY]
   │                                                  │
   │            0x07 ────────────────────────► configure_eprom() [eprom.cpp]
   │                                              eprom_write_execute(): VPP regulator
   │                                              ON + VPE_DROP → CTRL_VPE pulse
   │                                              (pulse_delay) → verify mask
   │                                              [DIFF = check_vpp+chip_id extraction
   │                                               ONLY; write_execute UNTOUCHED]
   │                                              FLAG_CAN_ERASE → auto-erase pulse
   │                                              (12V VPP, A9+VPE) before program
   │                                                  │
   │     DATA chunks ◄─── ack-paced ──────────►  poll_readback (P5) / verify_and_update_mask
   │                                              [P5 byte-identical to old flash4 loop;
   │                                               flash4 PASSED with it]
   │
   └─ verify <chip> <img> → re-read → SHA == image?  ◄── the byte-identity gate
```

The diagram's load-bearing point: **every box on the 0x06/0x07 write path is marked UNCHANGED or behavior-preserving.** The only boxes with a behavioral delta in the recompose belong to OTHER protocols (none of which is on these two chips' write path).

### Pattern 1: Controlled single-axis A/B (the RCA's core method)
**What:** Hold all-but-one variable fixed, swap one axis, re-run the identical write-cycle, compare SHA.
**When to use:** Attributing a regression across two repos (fw + host) where both moved.
**Axes (in priority order):**
1. **Firmware axis** (decisive, in scope now): reflash `a1953c2` (b10) with current host `e46549f` → re-run SST39SF040 write-cycle.
   - b10 fw **PASSES** ⇒ regression is firmware (recompose). (CONTEXT's expected outcome; this research rates it LOW probability given zero write-path delta.)
   - b10 fw **FAILS identically** ⇒ recompose is innocent; fault is host or bench/chip-state. (HIGH probability per the diff evidence.)
2. **Host axis** (in scope now, cheap — no reflash): with recompose fw `a296195` already flashed, `pip install -e .` the v1.15 host `98b3a92` and re-run the SST39SF040 write-cycle.
   - v1.15 host **PASSES** ⇒ regression is host. (Rated LOW — `eprom_operations` write path + DB entry are unchanged.)
   - v1.15 host **FAILS** ⇒ host innocent; converges on bench/chip-state/pre-existing.
3. **Bench/chip-state axis** (the residual): if both code A/Bs fail, the cause is environmental — VPP rail behavior under load, chip wear/state, erase-rail (the v1.14 `dev reg 0 0 0x86 -f` hold trick), or the flash3 slow-path timeout window.

### Pattern 2: Worktree-based b10 build without losing the recompose
**What:** Build the b10 firmware in a detached git worktree so HEAD on the v1.16 branch is never moved.
**Example:**
```bash
# Source: git worktree docs + project layout (firestarter is a submodule, HEAD=a296195)
cd /workspaces/firestarter
git worktree add /tmp/fs-b10 a1953c2          # detached b10 tree, recompose HEAD untouched
cd /tmp/fs-b10 && pio run -e leonardo         # build b10 image
pio run -t upload -e leonardo                 # flash b10 (Leonardo, chip may stay seated)
# ... run b10 A/B ...
cd /workspaces/firestarter && pio run -t upload -e leonardo   # restore recompose fw
git worktree remove /tmp/fs-b10
```
**Why worktree over branch-stash:** the sub-repo HEAD must stay at `a296195` (the firmware-under-test identity and the gitlink the meta pins); a worktree builds b10 in isolation with zero risk to the recompose checkout or uncommitted work.

### Pattern 3: Confirm firmware identity at every swap
**What:** `firestarter fw` reports `3.0.0b10` for BOTH builds (version string was not bumped at Phase 84 — D/version_string_caveat). The version string does NOT distinguish the recompose from stock b10.
**How to disambiguate which image is actually on the board:** the Leonardo flash byte count is the only reliable in-band discriminator — recompose `a296195` = **25136 B / 87.7%**; baseline b10 `a1953c2` = **25654 B** (per `89-FLASH-LEDGER`, −518 B net). Record the `pio run` flash-size line for each build and the avrdude "bytes written" on each upload as the identity proof, alongside `firestarter fw`.

### Anti-Patterns to Avoid
- **Assuming the reflash-b10 A/B will clear the chip.** The diff evidence says it almost certainly will NOT. Planning the fix as "the A/B confirms recompose, then revert the recompose" is the wrong default — it has no code target (nothing on the write path changed to revert).
- **Reading "12V-VPP write path" literally for 0x06.** SST39SF040/flash3 is **5V-only; it never enables the VPP regulator** (`firestarter/CLAUDE.md` handler table: 0x06 = "None (5V)"; BLOCKER-2 keeps it off `configure_eprom`). The DB `vpp:"12V"/vpp_mv:12000` field is a minipro-decode artifact, NOT a routed rail. The "12V-VPP axis" is a *correlational label* for the two failing flash/EPROM writes, not a shared mechanism — CONTEXT itself notes "a P3-only explanation does NOT cover both."
- **Using `dev write-cycle`.** It blank-checks/erases first and fails on flash; use the v1.15 `write -b` direct path (CONTEXT-locked).
- **Treating W27C512 `bad bytes:N` as a transport/firmware bug.** Project memory (`reference_w27c512_bench_write_erase_gotcha`): a non-blank W27C512 cannot flip 0→1 without an erase; "bad bytes:921/1024" actually *confirms* the transport delivered a full block. It is a chip-state failure.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Diffing the write path | A bespoke scanner | `git diff a1953c2..a296195 -- src/proms/<file>` | Already done in this research; cite the hunks. |
| DB wire-param comparison | Manual JSON eyeballing | `git show <rev>:firestarter/data/chip_database.json \| python3` extract by `part_number` | Done here; both chips byte-identical. |
| b10 build isolation | Stash/branch juggling on the live submodule | `git worktree add /tmp/fs-b10 a1953c2` | Zero risk to the recompose HEAD/gitlink. |
| Firmware identity check | Trusting the version string | flash byte count (25136 vs 25654) + `firestarter fw` | Version string is `3.0.0b10` for both. |
| VPP rail diagnostics | A new measurement script | `firestarter vpp` / `vpe` continuous monitors (capture via `timeout -s INT 15 stdbuf -oL ... vpp`) | Measure-only, safe with chip seated; project-standard. |
| Holding the erase rail for a DMM | Custom register pokes | `firestarter dev reg 0 0 0x86 -f` (v1.14 reusable) | Documented hold-rail technique. |

**Key insight:** Every tool needed to adjudicate this RCA already exists; the phase is forensic + bench-procedural, not constructive. The hand-roll risk here is *inventing a fix for a non-existent code regression*.

## Runtime State Inventory

> This phase is an RCA + bench validation, not a rename/refactor. The "runtime state" that matters is bench/board/chip state, captured here because it is the leading suspect once the code A/Bs come back innocent.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data (on-chip) | SST39SF040 currently holds wrong `ebca6266…` content; W27C512 holds partial `ce12c20a…` (from Phase 90). Both are rewritable. | Overwriting during fix-validation is EXPECTED and authorized (CONTEXT). The wrong content is itself an RCA datapoint (deterministic ⇒ a stable mechanism, not noise). |
| Live board state | Leonardo flashed with `a296195` (recompose, 25136 B). Flashing b10 replaces it; restore recompose afterward. | A/B reflash protocol (Pattern 2); `firestarter fw` + flash-byte-count check each swap. |
| Host install state | `firestarter` CLI installed from `e46549f` (v1.16). Host-axis A/B requires `pip install -e .` of `98b3a92`, then re-install `e46549f`. | Re-install the v1.16 host after the host-axis A/B so the bench returns to the documented config. |
| VPP/erase rail state | v1.15 W27C512 needed an operator VPP correction (13.1V→12.0V) before its clean write; Phase 90 had a clean 12.0V *idle* rail but failed. Rail behavior **under write load** was not measured. | Capture `firestarter vpp` during/around a write attempt (or hold via `dev reg 0 0 0x86 -f`) — idle-clean ≠ loaded-clean. |
| Build artifacts | `/tmp/fs-b10` worktree + its `.pio/` build dir (b10 image). | `git worktree remove /tmp/fs-b10` after the A/B; do NOT commit the b10 build. Gitlinks stay PINNED at b10 (D-06). |

**Nothing found in category — secrets/env vars:** None — verified by inspection; no secret or env-var name participates in the write path.

## Common Pitfalls

### Pitfall 1: "The recompose broke it" anchoring
**What goes wrong:** Planning the fix as a recompose revert.
**Why it happens:** The phase title says "regression," Phase 90 ran on recompose fw, and P3 (`vpp_check_window`, −402 B) is the biggest recompose change.
**How to avoid:** The diff proves P3's body is byte-identical to the original `eprom_check_vpp` block, and `eprom_check_vpp` is a VPP *measurement/guard* function — it does not program cells. flash3 (0x06) has no P3 *and no code change at all*. Run the b10 A/B before committing to any code target.
**Warning signs:** A plan task that says "revert P3" or "restore the old check_vpp" — there is nothing to restore; the body is identical.

### Pitfall 2: Reading idle VPP as proof of a healthy write rail
**What goes wrong:** "Rail was a clean 12.0–12.1V" is taken to exonerate the rail.
**Why it happens:** Phase 90 measured `firestarter vpp` (idle/monitor), which is measure-only and does not route to the socket.
**How to avoid:** The program pulse draws current; a regulator that sags under load reads clean idle. Measure around/under load, or hold the rail with `dev reg 0 0 0x86 -f` for a DMM.
**Warning signs:** Bad-bytes clustered at write-start (W27C512: first ~921 B) — consistent with a rail that hasn't fully settled/holds under the initial erase+program burst.

### Pitfall 3: Flash3 slow-path vs host timeout window (the SST39SF040 write-A timeout)
**What goes wrong:** "write A: Operation timed out (RC=1)" read as a firmware hang.
**Why it happens:** v1.15 EVIDENCE notes "flash3 slow path ~240s/write" for the 524288 B SST39SF040; Phase 90's write-B that *completed* took ~177s. A write-A that erases-then-programs can exceed the host's per-operation response window, surfacing as a firmware-level timeout even though the chip is still working.
**How to avoid:** Treat the write-A timeout + the deterministically-wrong (but internally-consistent) write-B content as TWO facets of one mechanism: a partially-completed/under-volted program that is reproducible because the rail/timing behavior is reproducible. The A/B (does b10 also time out?) discriminates.
**Warning signs:** Deterministic wrong content (`ebca6266…` identical across reseats) — a stable hardware/timing mechanism, not random corruption.

### Pitfall 4: W27C512 "bad bytes" mistaken for a write-path code fault
**What goes wrong:** `bad bytes:921 @0x000000` read as a 0x07 firmware regression.
**Why it happens:** It's reproducible across reseat at a clean idle rail.
**How to avoid:** Per project memory, a non-blank W27C512 can't flip 0→1 without a working erase; "bad bytes:N/1024" confirms a full block was delivered. W27C512 carries `FLAG_CAN_ERASE` (EEPROM type) in BOTH v1.15 and v1.16 host (verified byte-identical), so the auto-erase pulse (12V VPP, A9+VPE) runs in both — if that erase pulse is under-volted/under-timed on this board, the program fails at write-start exactly as observed. This is a rail/erase-pulse hypothesis, not a code-diff hypothesis.
**Warning signs:** Failure localized to the start of the address space; clean read path (read uses no VPP/erase).

## Code Examples

### A/B build + flash + identity (firmware axis)
```bash
# Source: firestarter/CLAUDE.md build commands + git worktree
cd /workspaces/firestarter
git worktree add /tmp/fs-b10 a1953c2
cd /tmp/fs-b10
pio run -e leonardo            # expect Flash ~25654 B (b10 baseline identity)
pio run -t upload -e leonardo  # Leonardo EXEMPT from chip-out; SST39SF040 may stay seated
firestarter fw                 # reports 3.0.0b10 (same string for both — use flash size to disambiguate)
```

### Write-cycle (the v1.15-faithful method, both axes)
```bash
# Source: 90-04-SUMMARY harness deviation + v1.15 EVIDENCE; CONTEXT-locked
firestarter write -b SST39SF040 /tmp/firestarter_bench_p90/SST39SF040_img_A.bin
firestarter verify  SST39SF040 /tmp/firestarter_bench_p90/SST39SF040_img_A.bin
firestarter write -b SST39SF040 /tmp/firestarter_bench_p90/SST39SF040_img_B.bin
firestarter verify  SST39SF040 /tmp/firestarter_bench_p90/SST39SF040_img_B.bin
firestarter dev consistency-check SST39SF040 --runs 3 --output-dir firestarter-runs/SST39SF040-ab/
# PASS = final SHA == v1.15 baseline a38b13b4d285756c1f385a75d0cdf89f72720764c21fd933ced75ebdd970b96b
```

### Host-axis A/B (no reflash; recompose fw stays on the board)
```bash
# Source: project memory reference_firestarter_app_python_test_env (use /usr/local python)
cd /workspaces/firestarter_app
git worktree add /tmp/fsa-b8 98b3a92      # v1.15 host
cd /tmp/fsa-b8 && pip install -e .
firestarter write -b SST39SF040 .../SST39SF040_img_A.bin   # ... full write-cycle ...
cd /workspaces/firestarter_app && pip install -e .          # restore v1.16 host e46549f
```

### Native Unity (no hardware) — what IS unit-testable
```bash
# Source: firestarter/CLAUDE.md Native Test Environment
cd /workspaces/firestarter
pio test -e native -f "*test_val_flash3*"   # flash3 0x06 write golden trace (bus sequence)
pio test -e native -f "*test_val_eprom*"    # eprom 0x07/0x08/0x0B write+chip-id golden traces
```

### VPP rail under load (the residual-axis diagnostic)
```bash
# Source: reference_v114_bench_erase_rail_and_test_artifact
timeout -s INT 20 stdbuf -oL firestarter vpp        # capture rail trace around a write
firestarter dev reg 0 0 0x86 -f                     # hold erase rail for a DMM reading
```

## State of the Art

| Old Assumption (CONTEXT prior) | Evidence-Corrected View | When Changed | Impact |
|--------------------------------|-------------------------|--------------|--------|
| Recompose (a296195) regressed the 12V-VPP write path | No write-path code delta exists in `a1953c2..a296195` for 0x06/0x07; the failing chips' DB entries are byte-identical v1.15↔v1.16 | This research (2026-06-26) | Reframes the fix from "revert recompose" to "adjudicate environmental/pre-existing via A/B." |
| The b10 A/B will clear SST39SF040 (firmware-caused) | b10 A/B most likely FAILS identically (recompose innocent) | This research | Plan must handle the "both A/Bs fail" branch as the primary path, not an edge case. |
| 0x06 is a "12V-VPP" write path | 0x06/flash3 is 5V-only; never enables the VPP regulator (BLOCKER-2). "12V-VPP" is a correlational label, not a shared mechanism | `firestarter/CLAUDE.md` + flash3 source | The two symptoms need two mechanisms; do not seek one shared code change. |

**Deprecated/outdated as an RCA target:**
- "P3 `vpp_check_window` regression" — P3's body is byte-identical to the original; flash4/FM1608/all-reads pass through the same primitive set. P3 is not a viable root cause for either symptom. (It remains worth *naming* in the writeup only to formally exonerate it.)

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The b10 reflash A/B will FAIL identically for SST39SF040 (recompose innocent). | A/B Pattern 1 / State of the Art | If b10 PASSES, the regression IS firmware-caused via some path the static diff didn't surface (e.g., compiler/codegen/layout-sensitive timing) — the plan's decision tree must still branch correctly, so this is bounded: the experiment decides, not the assumption. |
| A2 | The SST39SF040 write-A timeout + deterministic-wrong write-B is a single under-volt/under-time program mechanism (rail-under-load or flash3 slow-path × host window). | Mechanism / Pitfall 3 | If the wrong content `ebca6266…` decodes to a *structured* corruption (e.g., a fixed offset/byte-swap), the mechanism could be addressing/buffer-related instead — a content forensic on `ebca6266…` vs image B should be a plan task to confirm/deny. |
| A3 | The W27C512 bad-bytes-@0x0 is an erase-pulse/rail issue (FLAG_CAN_ERASE auto-erase under-performing on this board), not code. | Pitfall 4 | If W27C512 writes clean under b10 fw, the auto-erase code path differs in some way the diff missed; but W27C512 bench is DEFERRED, so this stays analysis-only this session. |
| A4 | `firestarter vpp` idle-clean does not prove the rail is clean under write load. | Pitfall 2 | Standard regulator behavior; low risk. If a loaded measurement also reads clean, the rail is exonerated and attention moves to chip wear/timing. |
| A5 | Worktree `git worktree add /tmp/fs-b10 a1953c2` builds b10 cleanly with the current PlatformIO/leonardo platform. | A/B Pattern 2 | If b10 fails to build under the current toolchain, fall back to `git stash` + `git checkout a1953c2 -- src/ include/` in a throwaway state, or build from a fresh clone at a1953c2. |

## Open Questions

1. **Does the deterministic wrong content `ebca6266…` have structure relative to image B?**
   - What we know: it is reproducible across reseats (stable mechanism); ≠ image B `a38b13b4…`.
   - What's unclear: whether it's a partial program (first-N-bytes correct), a constant fill, or a transformed image.
   - Recommendation: add a plan task to byte-compare the post-fail capture (`bench/SST39SF040-wcB/run_01.bin`) against image B and quantify where/how it diverges — this discriminates A2 (timing/rail) from an addressing/buffer fault.

2. **Does b10 fw write SST39SF040 clean, fail-identically, or fail-differently?**
   - What we know: code is unchanged; b10 is the v1.15 baseline that PASSED in v1.15.
   - What's unclear: whether the *board/chip* is in the same state as v1.15 (chip wear, regulator drift).
   - Recommendation: this IS the decisive experiment — run it first, record the exact `write -b` outcome + timing + a loaded `vpp` capture.

3. **Was the v1.15 SST39SF040 PASS reproducible at N>1, or a single clean run?**
   - What we know: v1.15 EVIDENCE shows write_A→write_B PASS with consistency-check N=3 *on readback*, ~240s/write.
   - What's unclear: whether v1.15 ever saw a write-A timeout that was retried.
   - Recommendation: note as context; the b10 A/B supersedes archival re-litigation.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO (`pio`) | fw build/flash + native tests | ✓ | 6.1.19 | — |
| Leonardo on `/dev/ttyACM0` | bench A/B (silicon) | ✓ (operator-confirmed) | fw `3.0.0b10` string | — (operator absent for chip swaps) |
| RURP shield Rev 2.0 | bench A/B | ✓ (operator silkscreen) | Rev 2.0 | — |
| SST39SF040 seated | 0x06 bench (in scope now) | ✓ (operator-measured) | — | — |
| W27C512 seated | 0x07 bench | ✗ (chip swap needs operator) | — | Defer 0x07 bench → operator checklist (CONTEXT-locked) |
| `firestarter` host CLI (e46549f + 98b3a92) | host-axis A/B | ✓ | v1.16 / v1.15 | `pip install -e '.[test]'` via `/usr/local` python if toolchain wiped |
| git worktree | b10 isolation | ✓ | — | stash/throwaway-clone fallback (A5) |

**Missing dependencies with no fallback:** None for the in-scope SST39SF040 work.
**Missing dependencies with fallback:** W27C512 silicon (operator-gated) → 0x07 stays analysis-only + ready-to-run checklist this session.

## Validation Architecture

> `workflow.nyquist_validation` is absent in `.planning/config.json` → treated as ENABLED. This section drives VALIDATION.md.

### Test Framework
| Property | Value |
|----------|-------|
| Framework (firmware) | PlatformIO Unity, `[env:native]` (host-side, no board) — `firestarter/platformio.ini` |
| Framework (host) | pytest (`firestarter_app`, `pip install -e '.[test]'`) |
| Quick run command | `pio test -e native -f "*test_val_flash3*"` (0x06 bus sequence) |
| Full suite command | `pio test -e native` (all native firmware suites) + host `pytest` |
| Silicon oracle | Leonardo + Rev 2.0 + SST39SF040; SHA byte-identity vs v1.15 baseline `a38b13b4…` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RCA-91 | flash3 0x06 write bus sequence unchanged by recompose | unit (native) | `pio test -e native -f "*test_val_flash3*"` | ✅ `test/native/avr/test_val_flash3/` |
| RCA-91 | eprom 0x07 write+chip-id sequence unchanged | unit (native) | `pio test -e native -f "*test_val_eprom*"` | ✅ `test/native/avr/test_val_eprom/` |
| RCA-91 | b10-vs-recompose attribution | bench A/B (manual, silicon) | `firestarter write -b SST39SF040 ...` under each fw | ❌ manual — record in BENCH-LOG (no automation possible without hardware) |
| RCA-91 | wrong-content `ebca6266…` structure forensic | host analysis | `python3` byte-compare of post-fail capture vs image B | ❌ Wave 0 (one-off forensic script) |
| FIX-91 | SST39SF040 write+verify == v1.15 SHA | bench gate (silicon) | `firestarter verify SST39SF040 img_B` + `dev consistency-check --runs 3` | ❌ manual — silicon-only |
| FIX-91 | host DB wire-param parity 0x06/0x07 v1.15↔v1.16 | unit/host | `git show <rev>:.../chip_database.json` extract + compare (done in research; pin as a test) | ❌ Wave 0 (pin as a regression assertion if a code fix lands) |
| FIX-91 | 0x06/0x07 PROTOCOL-LEDGER rows dispositioned + checker green | host | `python3 .planning/.../check_ledger.py` (Phase 90-01) | ✅ `check_ledger.py` exists |

### Sampling Rate
- **Per task commit:** the relevant native suite (`pio test -e native -f "*test_val_flash3*"` and/or `*test_val_eprom*`) — sub-30s, no board.
- **Per wave merge:** full `pio test -e native` + host `pytest` + `check_ledger.py`.
- **Phase gate:** SST39SF040 bench write+verify byte-identical to `a38b13b4…` (the silicon truth); ledger checker RC=0.

### Wave 0 Gaps
- [ ] One-off forensic: byte-compare `bench/SST39SF040-wcB/run_01.bin` (`ebca6266…`) vs `SST39SF040_img_B.bin` — covers RCA-91 Open Q1 (no test file today).
- [ ] If a host code/DB fix lands: a pytest assertion pinning the 0x06/0x07 wire-param parity (currently only proven ad-hoc in research) — covers FIX-91.
- [ ] No framework install needed — native Unity + pytest infra already present (Phase 88 golden traces + Phase 90 `check_ledger.py`).
- *Note:* the firmware-causality verdict is **bench-only** (real silicon SHA gate); native Unity can only prove the *bus sequence* is unchanged, not that the rail/timing on real hardware succeeds. This is the irreducible HIL gap and must be stated in VALIDATION.md.

## Security Domain

> `security_enforcement` is absent in `.planning/config.json` (= enabled by default). This phase issues no network/auth/input-parsing changes; it is a local-hardware RCA. The relevant safety posture is HARDWARE safety (12V/VPP routing), already enforced and unchanged.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | partial | The firmware VPP over-voltage guard (`vpp_mv > handle->vpp_mv + 500`, `primitives.cpp:106`) is the hardware-safety input-validation control — PRESENT + UNMODIFIED (SAFE-04). Do not weaken it during the RCA. |
| V6 Cryptography | no | SHA-256 used only as a byte-identity oracle, not a security primitive. |

### Known Threat Patterns for this stack (hardware-safety framing)
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| 12V VPP routed to a 5V-only part (flash3/SRAM) | Tampering / destruction | `configure_memory` protocol-prefix dispatch keeps 0x06/SRAM off `configure_eprom`; BLOCKER-2 invariant (UNCHANGED). |
| VPP over-voltage during program | Tampering / hardware damage | `vpp_check_window` HIGH check +500mV threshold (D-08, UNMODIFIED). |
| Forcing past safety guards (`-f`) during the A/B | Elevation (of risk) | `-f` bypasses the VPP-high init guard; documented as conservative-on-this-board (memory), but use only as the operator standing directive allows; never weaken the firmware guard itself. |

## Sources

### Primary (HIGH confidence)
- `git diff a1953c2..a296195` (firestarter) — write-path forensics: `src/proms/eprom.cpp` (check_vpp+chip_id extraction only; `eprom_write_execute` untouched), `src/proms/flash_type_3.cpp` (comment-only), `src/proms/flash_type_4.cpp` (poll_readback extraction; PASSES), `src/proms/primitives.cpp` + `include/primitives.h` (P3/P4/P5 bodies byte-identical to originals), `src/proms/flash_utils.cpp`/`include/flash_utils.h` (dead `FLASH_ENABLE_WRITE_PROTECTION` delete, zero callers).
- `git diff 98b3a92..e46549f` (firestarter_app) — host forensics: `firestarter/eprom_operations.py` (cosmetic output-dir + SRAM-only short-circuit), `firestarter/database.py` (FLAG_CAN_ERASE derivation refactor, predicate identical v1.15↔v1.16), `firestarter/data/chip_database.json` (SST39SF040 + W27C512 entries byte-identical).
- `.planning/v1.16/ledger/bench/BENCH-LOG.md` — exact failure strings, SHAs, rail readings, reseat reproducibility.
- `.planning/v1.15/bench/EVIDENCE.md` rows 1/5 — v1.15 W27C512 + SST39SF040 write PASS (same Leonardo+Rev2.0), the SHAs Phase 90 failed to reproduce, the "flash3 slow path ~240s/write" + "W27C512 initial VPP-high 13.1V corrected" notes.
- `firestarter/CLAUDE.md` — handler/VPP table (0x06 = None/5V; 0x07 = 13V via VPE_DROP), dispatch order, native test invocation.
- Verified this session: `pio --version` (6.1.19), `firestarter` worktree clean at `a296195`, host at `e46549f`.

### Secondary (MEDIUM confidence)
- Project memory `reference_w27c512_bench_write_erase_gotcha` — "bad bytes:N is chip-state not transport"; erase unsupported on 0x07 standalone; use `-b`.
- Project memory `reference_v114_bench_erase_rail_and_test_artifact` — `dev reg 0 0 0x86 -f` rail hold; `vpp` continuous-monitor capture idiom.
- Project memory `project_v116_protocol_rebuild_seed` / `89-FLASH-LEDGER` — recompose flash-size identity (25136 B vs 25654 B), version-string-not-bumped caveat.
- Project memory `reference_firestarter_app_python_test_env` — `/usr/local` python, `pip install -e '.[test]'`.

### Tertiary (LOW confidence)
- None — all claims are grounded in the diffs, the bench ledgers, or verified tool output.

## Metadata

**Confidence breakdown:**
- Diff/wire-param facts (no write-path delta; DB entries identical): HIGH — directly read from both repos' git history this session.
- Leading hypothesis (environmental/pre-existing, not recompose): MEDIUM — strongly implied by the absence of any code delta + flash4/FM1608/all-reads passing through the same primitives; the bench A/B is the confirming experiment.
- Both-symptom mechanism (under-volt/under-time program; W27C512 erase-rail): MEDIUM — consistent with v1.15 notes + project memory, pending the loaded-rail measurement and the `ebca6266…` content forensic.
- A/B procedure + tooling: HIGH — commands verified against `firestarter/CLAUDE.md` and tool availability.

**Research date:** 2026-06-26
**Valid until:** stable while the firmware HEAD stays `a296195` and host stays `e46549f` (~30 days); invalidate immediately if either submodule advances.
