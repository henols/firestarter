# v1.34 — Close Record: Evidence Table, Merge Recommendation & Honesty Ledger

**Milestone:** v1.34 Pre-Merge Hardware Regression Validation
**Closed:** 2026-08-29, by operator direction ("stop testing, close ASAP")
**Discharges:** CLOSE-01…05, RCA-01…05
**Status of this close:** **EARLY / SCOPE-REDUCED.** This is not a completed sweep. Read
§1 before reading anything else.

---

## 1. Scope — what ran, and what did not

The operator directed on 2026-08-29 that bench testing stop and the milestone close on the
evidence already banked. This section exists so no later reader mistakes this for a full sweep.

| Phase | Planned | Actually executed | Status |
|---|---|---|---|
| 160 RIG | dual-arm build, flash provenance, cell procedure | all of it | **complete** |
| 161 BOARD | 12 positions (3 boards × 2 arms × 2 chips) | **12 of 12** | **complete** |
| 162 CHIP | 11 parts × v133 arm, + control re-run per divergence | **5 of 11 parts** + 1 control re-run; plans 1–7 of 10 | **PARTIAL — stopped by direction** |
| 163 SHIELD | 8 positions (Rev 2.2 + Modified Rev 0) | **nothing** | **NOT RUN** |
| 164 REV0 | Modified Rev 0 rework trace + photography | **nothing** | **NOT RUN** |
| 165 RCA | regression triage, root cause, PR-branch fix | discharged on the evidence that exists (§3) | **complete for what was measured** |
| 166 CLOSE | this document | this document | **complete** |

**The six chips never swept:** ST M27C512, SST39SF040, W29C040, W29C020, AM27C020, 2516.
**The two shields never swept:** Rev 2.2, Modified Rev 0. Every v1.34 result therefore comes
from **Rev 2.0 only**.

---

## 2. CLOSE-01 — Evidence table

Every position holds a result or a named reason for its absence. No silent gaps.

### 2.1 Board sweep (Phase 161) — 12 of 12 present

| Cell | Board / shield | Arm | W27C512 | W29C020 |
|---|---|---|---|---|
| A1 | Uno / Rev 2.0 | control | recorded | recorded (milestone's first 262144 B write+read on silicon) |
| A1 | Uno / Rev 2.0 | v133 | recorded (N=3 reads agree) | recorded (N=3 reads agree) |
| A2 | uno328pb / Rev 2.0 | control | recorded — program-phase failure **observed** | recorded — failure observed |
| A2 | uno328pb / Rev 2.0 | v133 | recorded — same failure, **both arms** | recorded — same failure, both arms |
| A3/B2 | Leonardo / Rev 2.0 | control | recorded | recorded |
| A3/B2 | Leonardo / Rev 2.0 | v133 | recorded (N=3 stable) | recorded (N=3 stable) |

Plus 4 bring-up rows (`BRINGUP-uno`, `-uno328pb`, `-leonardo`, `-wrv`) proving the read chain,
the judged-span policy, Leonardo bootloader-entry behaviour, and the first clean
write-read-verify on real silicon.

### 2.2 Chip sweep (Phase 162) — 5 of 11 parts

| Part | Size | Arm | Result | Note |
|---|---|---|---|---|
| W27C512 | 0x10000 | v133 | **PASS** — all six executed steps OK | |
| W27E512 | 0x10000 | v133 | **PASS** per operator ruling | known stuck bit @0x3d (D-32 silicon wear, CHIP-05) |
| SST27SF512 | 0x10000 | v133 | **PASS** — all six executed steps OK | |
| FM1608 | 0x2000 | v133 | **PASS** per operator ruling | live PASS superseded D-03's pre-booked divergence |
| W27E040 | 0x80000 | v133 | **FAIL** — blank-check, `Empty input` (164/0xA4) | root-caused, see §3.1 |
| W27E040 | 0x80000 | **control** | re-run — **CONFIRMS NOT a v1.33 regression** | CHIP-04 divergence re-run |

| Part | Reason for absence |
|---|---|
| ST M27C512, SST39SF040, W29C040, W29C020, AM27C020, 2516 | **Not run — sweep stopped by operator direction 2026-08-29.** No result is claimed or implied for any of them. |

### 2.3 Shield sweep (Phase 163) and REV0 (Phase 164)

| Position | Reason for absence |
|---|---|
| B3 (Leonardo / Rev 2.2) × 2 arms × 2 chips | **Not run** — phase never started; stopped by direction |
| B1 (Leonardo / Modified Rev 0) × 2 arms × 2 chips | **Not run** — phase never started; stopped by direction |
| REV0-01…03 (photography, rework trace, ten TBD cells) | **Not run.** The ten `TBD pending Phase 35` cells in `v1.7-SHIELD-REVS.md` §4/§5 **remain TBD**, now pending a future milestone rather than Phase 35. |

---

## 3. RCA — regression triage (RCA-01…05)

### 3.1 The one hard failure: W27E040 blank-check `Empty input` — **PRE-EXISTING, FIXED**

**RCA-01 classification: pre-existing.** **RCA-02: not v1.33-caused, so no v1.33 change to
attribute.** The A/B evidence naming this:

- The control-arm re-run at position 5 reproduced the same failure (`CHIP__v133__w27e040.control-rerun`).
- Source proof added 2026-08-29: `git log 8695ee5..5759dc8 -- src/operation_utils.cpp
  src/proms/memory.cpp` shows v1.33 touched those files nine times but **never** the
  emit/ack structure, and `git show 8695ee5:src/operation_utils.cpp` carries the
  byte-identical `LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, …)` with no `op_wait_for_ack`
  after it. The defect is in **both arms**.

**Root cause (full record: `.planning/debug/resolved/blank-check-empty-input-98pct.md`):**
standalone blank-check emitted one `MSG_DATA_PROGRESS` per 2048 B chunk but never consumed the
host's per-frame ack, so the firmware ran unthrottled for the whole operation without touching
the incoming byte stream. Past roughly 4–5 KB of cumulative TX, `handle->cmd` reverted to
`CMD_IDLE` outside `command_done()`, and the idle branch decoded the unread backlog into the
overloaded `MSG_ERR_EMPTY_INPUT`. Deterministic at 251/256 chunks on a 512 KB part.

**RCA-03 — fixed on the v1.33 PR branch**, even though it is pre-existing rather than
v1.33-caused, because the PR was open and the fix belongs with the code it repairs:
- `1e8bbae` — consume the host ack after the progress emit.
- `a218b4f` — widen `BLANK_CHECK_CHUNK_SIZE` 2048 → 8192, cutting a 512 KB part from 256
  frames + 256 round-trips to 64 of each at zero added instructions.

**Re-validated in the cell that caught it** (RCA-03's second clause): on the same Leonardo,
same W27C040/W27E040 database row, blank check went 4/4 clean at 59.66–59.68 s with the bar
advancing smoothly and landing exactly on `0x80000/0x80000`; not-blank still correctly reported
as `MSG_ERR_NOT_BLANK` with its offset+value payload; `write` / `verify` / `erase` all clean.
Cost **+16 B flash on all three AVR targets, +0 RAM**; the `--policy merge05` growth guard
stays green with large margin (leonardo `-1792<=724`).

**Scope limit, stated rather than glossed:** this fix is **not** in either pinned arm image.
The bench board was restored to the v133 arm (`5759dc8`) and proven so by independent avrdude
read-back (`judged_match=True`, 25098 B). Every v1.34 measurement was taken **without** the fix.

### 3.2 Same error text elsewhere in the sweep — **INCONCLUSIVE** (RCA-04)

The identical `ERROR: Empty input` text appeared, at differing steps and without changing the
step verdict, on `CHIP__v133__w27c512`, `CHIP__v133__w27e512`, the superseded
`CHIP__control__w27e512`, and `CHIP__v133__sst27sf512`.

**These are NOT explained by §3.1.** All three parts are 64 KiB = 32 chunks ≈ 544 B of
cumulative TX — an order of magnitude below the ~4–5 KB threshold that triggers that defect.
**Recorded as inconclusive and not resolved by assumption in either direction.** Phase 162-07's
earlier reading of the whole cluster as "intermittent, arm-independent frame corruption" is
**superseded for the 512 KB case only**; for these 64 KiB occurrences it remains an
unexplained, unreproduced observation. Filed — see §6.

### 3.3 A2 uno328pb program failures — **PRE-EXISTING** (RCA-01, RCA-05)

Captured on **both** arms rather than assumed (BOARD-02's whole point). Linked to backlog
**999.2** (uno328pb program-path brownout hang). **Explicitly not fixed in v1.34.**

### 3.4 Ratiometric VPP ADC error — **PRE-EXISTING, INCONCLUSIVE as to mechanism** (RCA-04)

Three paired firmware-vs-multimeter readings across two independently calibrated boards cluster
near **+7.5 % (range 6.8–8.3 %)**, consistent with — **not proven as** — a shield-wide
gain/divider fault rather than per-board EEPROM miscalibration. Arm-independent; nothing about
it is v1.33-attributable. It materially **weakens** A2's leading low-VPP hypothesis for its four
write failures. Not resolved here. Filed — see §6.

### 3.5 `~/.firestarter/config.json` writes despite `FIRESTARTER_CONFIG_DIR` — **PRE-EXISTING**

Three recurrences across A1, A2 and A3/B2 (mtime-only; content byte-identical to baseline). The
harness audited clean; the leak is in `ConfigManager`. Arm-independent. Not fixed in v1.34. Filed.

### 3.6 RCA-01 completeness statement

**Zero v1.33-caused regressions were found in any position actually measured** — 12 board
positions and 6 chip-sweep rows. Every failure encountered classified as pre-existing or
inconclusive, with its A/B evidence named above. **RCA-02 is therefore vacuously satisfied:
there was no v1.33-caused regression to root-cause.** That is a real result, but it is a result
about the positions measured, not about the six chips and two shields never swept.

---

## 4. CLOSE-02 — Merge recommendation

# MERGE WITH CAVEATS

**The recommendation.** Merge `firestarter_prom#43`, `firestarter#56` and `firestarter_app#54`
to `beta`.

**The evidence it rests on:**
1. **12 of 12 board positions** completed across three boards × two arms × two chips. No
   v1.33-attributable divergence in any of them.
2. **5 of 11 chips** swept on the v1.33 arm: four PASS, one FAIL.
3. **The single FAIL was proven pre-existing** by both a control-arm re-run and direct source
   comparison of the two arms, then root-caused to a specific mechanism and fixed on the PR
   branch (§3.1).
4. v1.33's headline size claim is independently corroborated: the live baseline re-record at
   Phase 158 and this milestone's own cold builds agree, and the growth guard against BASE-01
   passes with roughly 1.8 KB of margin.

**The caveats this recommendation is explicitly conditioned on:**
- **C-1.** Six of eleven chips were never swept. Among them are three parts with known prior
  trouble — SST39SF040, W29C040 (permanently locked boot block, CR-01) and AM27C020
  (non-deterministic marginality). No claim is made about any of them under v1.33.
- **C-2.** Two of three shields were never swept. **Every result in this milestone is Rev 2.0.**
  v1.33 merges with zero bench evidence on Rev 2.2 and Modified Rev 0.
- **C-3.** The 64 KiB `Empty input` occurrences (§3.2) are unexplained. They did not change any
  step verdict, but they are not closed.
- **C-4.** No electrical claim — see §5.
- **C-5.** The two fix commits were **not** present during any measurement in this milestone.

**Why not "merge" outright:** C-1 and C-2 leave more than half the planned evidence base
unmeasured. **Why not "do-not-merge":** every position that *was* measured came back clean of
v1.33 attribution, and the one hard failure was affirmatively shown to predate v1.33 by two
independent methods. Withholding a merge on evidence that never contradicted it would be
overcaution, but calling it "validated" would be overclaiming. Hence the middle verdict.

---

## 5. CLOSE-03 — Honesty ledger

Each claim paired with its explicit non-claim.

| # | What v1.34 claims | What v1.34 explicitly does NOT claim |
|---|---|---|
| H-1 | No v1.33-attributable regression in 12 board positions + 6 chip rows | That v1.33 is regression-free. Six chips and two shields were never measured. |
| H-2 | The W27E040 blank-check failure is pre-existing, root-caused and fixed | That the fix was exercised during this milestone's measurements. It was not — every arm image predates it. |
| H-3 | The fix is verified on a W27C040/W27E040 | That it is verified on any other part. Second-chip confirmation remains open; a chip swap is operator-only. |
| H-4 | The VPP ADC error is ratiometric across two boards at ~+7.5 % | That it is a shield-wide gain/divider fault. Three data points are *consistent with* that, not proof of it. |
| H-5 | Board identity was verified per cell by avrdude signature | That any firmware-reported field can identify a board or shield. It cannot — `hw_revision` collides across the operator's three shields. |
| H-6 | Read chains and write-read-verify were SHA-judged on silicon | **That program-window VPP/VCC under load was measured. IT WAS NOT.** The DTR-reset-on-close tooling gap stands unresolved. **v1.34 makes no electrical claim whatsoever.** |
| H-7 | A2's program failures reproduce on both arms | That their cause is established. Low-VPP was the leading hypothesis and H-4 substantially weakens it. Undetermined. |
| H-8 | The A2 N=3 read-instability question got a non-resolving data point | That it is resolved. It is **UNDETERMINED**. |
| H-9 | 4 of 5 swept chips PASS on the v1.33 arm | That those four PASSes were A/B-contrasted. Only the diverging chip (W27E040) got a control re-run, per CHIP-04. |
| H-10 | This close was directed by the operator | That the planned evidence base was completed. It was not; see §1. |

---

## 6. CLOSE-05 — Filed, not carried as prose

Everything found and not fixed is filed as a backlog item rather than left in this document:

| Finding | Filing |
|---|---|
| 64 KiB `Empty input` occurrences, unexplained (§3.2) | **new backlog item** — see `.planning/backlog/` |
| Ratiometric ~+7.5 % VPP ADC error (§3.4) | **new backlog item** |
| `~/.firestarter/config.json` written despite `FIRESTARTER_CONFIG_DIR` (§3.5) | **new backlog item** |
| `MSG_ERR_EMPTY_INPUT` (0xA4) is overloaded — no distinct `MSG_ERR_BAD_FRAME` | **new backlog item** (needs a `messages.toml` catalog entry + codegen) |
| `diagnostic_report.py` does not export `read_divergence` / total / bad / bad_pct / evidence | **new backlog item** |
| `size_baseline.json` live figures stale by +16 B on all three targets | **new backlog item** — land-time re-record with the fixture-severance pattern |
| Six unswept chips + two unswept shields + REV0 trace | **new backlog item** — the unfinished v1.34 sweep |
| uno328pb program-path brownout | existing **999.2** (RCA-05) |
| W29C040 locked boot block | existing **CR-01** (RCA-05) |

---

## 7. CLOSE-04 — Deviation, recorded rather than hidden

CLOSE-04 as written reads: *"v1.34 performs no merge, no push to `beta`, no sub-repo tag, no
beta cut and no release — every outward-facing step is left to the operator."*

**This close deviates from that requirement, by explicit operator instruction on 2026-08-29.**
Asked directly whether closing should also merge the three v1.33 PRs, the operator answered
"Yes — merge as part of the close," having been told in the same exchange that the step is
outward-facing and auto-fires a beta pre-release cut.

The requirement's purpose — that no outward-facing step happens without the operator's
decision — is **satisfied**: the operator made the decision. The requirement's letter — that
v1.34 performs no merge — is **not**. Recorded here as a deviation rather than marked complete,
so the ledger stays honest.

**Not performed even so:** no sub-repo tag, no stable release. Only the three PR merges to
`beta`, and the pre-release cut those merges fire on their own.
