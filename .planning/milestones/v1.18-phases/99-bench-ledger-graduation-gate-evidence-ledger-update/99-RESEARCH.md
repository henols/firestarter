# Phase 99: BENCH + LEDGER — Graduation Gate, Evidence & Ledger Update — Research

**Researched:** 2026-07-01
**Domain:** Operator-in-the-loop hardware bench validation (AM27C020 `0x08` write→verify graduation) + evidence capture + PROTOCOL-LEDGER update with a machine-checked consistency gate
**Confidence:** HIGH (all findings verified against repo artifacts, source code, and a live `check_ledger.py` run; no external packages, no training-data guesses)

---

## Summary

Phase 99 is the empirical closer for v1.18. Phases 97 (RCA) and 98 (FIX) are DONE and verified. Phase 98 landed a corrected `0x08` 32-pin write-path fix (`DIP32_27C020` pinout with `rw-pin:[31]` → `CTRL_READ_WRITE` 0x40, revision-invariant) that is native-green (119/119) and golden-trace byte-identical, but was **explicitly not bench-tested** — Phase 99 is "the sole empirical silicon gate." The phase has three deliverables: BENCH-01 (a bench-witnessed write→verify graduation OR a clean documented deferral), BENCH-02 (a per-chip EVIDENCE record), and the PROTOCOL-LEDGER `0x08` update from `open-defect-carried (FUT-06)` to its true post-bench status, with `check_ledger.py` passing at 0 contradictions.

The single most important finding is a **schema tension in `check_ledger.py`**: its D-09 PASS constraint (`_assert_ledger02_d09`) requires that any row with `verification_status == "PASS"` carry `evidence.p90_read_sha_matches_v115 == true` AND `evidence.p90_writecycle_sha_matches_v115 == true`. Those two flags encode "matches the v1.15 baseline." AM27C020 has a v1.15 *read* baseline but its v1.15 *write* was the 0-bits failure — there is **no v1.15 write-cycle baseline to match**. A naive `PASS` status will therefore either fail the gate or force a dishonest `true` flag. The plan must resolve this deliberately: the cleanest path is a schema/gate extension that recognizes a *v1.18-native* graduation (SHA self-consistency of the written image vs. read-back, not "matches v1.15"), applied only to the `0x08` row, with the gate script and its own unit tests updated in lockstep. This is a first-class planning task, not an afterthought.

The second key finding is the **automation boundary**. Almost everything except the physical silicon act is scriptable by the executor: SHA computation, test-image generation, ledger JSON/MD edits, running `check_ledger.py`, and evidence-file authoring. What *requires the operator at the bench*: seating the chip, adjusting the VPP pot, taking DMM readings at socket pin 1, confirming `controller:` identity and Rev 2.0 silkscreen, and authorizing each live write. The `dev write-cycle` harness that graduated the other chips **cannot be used** here because it erases first and AM27C020 is a UV EPROM with no electrical erase — the graduation must be a manual `write -b` (skip blank-check; the chip is NOT-BLANK) → `verify`/read-back → independent SHA compare. This mirrors exactly the method Phase 97 used to capture the failure signature.

**Primary recommendation:** Plan two mutually exclusive branches gated on the Phase-99 bench outcome (writable→graduate, or OTP/dead→defer), both driving the *same* EVIDENCE.json cell schema and the *same* ledger-update task. Add an explicit "extend `check_ledger.py` + its tests to admit a v1.18-native `0x08` PASS (or a new documented status) without a v1.15 write baseline" task, because the current gate structurally cannot pass a graduated `0x08` row. Front-load a hardware-availability + `controller:` identity + R1/R2 readback + VPP-pot-set operator checkpoint before any spend.

---

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| BENCH-01 | Full write→verify on seated AM27C020 (Leonardo + Rev 2.0) reads back byte-exact (SHA match) — the graduation gate. Contingent on PRE-01; if OTP/dead, defers to FUT with documented evidence (never faked). | §Host Commands (write -b → verify → SHA compare); §Decision Structure (graduate vs defer); §Common Pitfalls P1 (dev write-cycle erases → unusable on UV EPROM); §Operator vs Automated split. |
| BENCH-02 | Bench EVIDENCE record: 1→0 program proof / failing-vs-fixed signature, VPP rail reading at socket pin 1 during program window, bench-discipline log row (port, shield rev, R1/R2 readback, `controller:` identity, firmware commit) — sufficient to update the LEDGER 0x08 entry. | §Evidence Capture; §EVIDENCE.json schema (reuse Phase-97 cell shape); §VPP measurement (held-rail proxy is tooling-blocked — see debug doc + hold_rail.py); §Bench-discipline row fields. |

*(BENCH-01/02 are the only two REQ-IDs assigned to Phase 99 per REQUIREMENTS.md traceability lines 73–74. The LEDGER update is Success-Criterion #3 in the ROADMAP Phase-99 detail — it is the mechanism by which BENCH-02 evidence lands in the canonical ledger, not a separate REQ-ID.)*

---

## User Constraints (from standing project context — no phase-99 CONTEXT.md exists)

> Phase 99 has **no CONTEXT.md** (`has_context: false` from init). The following are standing, project-locked constraints (STATE.md, REQUIREMENTS.md, MEMORY.md) that bind this phase with the same authority as locked decisions. They are NOT open for the planner to re-explore.

### Locked Decisions (standing)

- **Bench LOCKED to Leonardo + RURP Rev 2.0.** No other board/shield. `[VERIFIED: REQUIREMENTS.md line 7]`
- **PRE-01 is the hard gate.** If the seated AM27C020 is OTP/dead, BENCH-01/02 defer to a FUT carry-forward and the milestone re-scopes to software-fix-only — **recorded as such, never faked.** `[VERIFIED: REQUIREMENTS.md line 8, 17, 33]`
- **SAFE invariant (recurs as a precondition through close):** over-voltage stays ERROR-blocked at the firmware VPP check (`primitives.cpp:106` `vpp_check_window`); host `chip_resolver.resolve_chip` guard never bypassed; AM27C020 flows through its normal `0x08` dispatch; no test-only escape hatch; `--force` is never passed. `[VERIFIED: REQUIREMENTS.md line 11, 38; STATE.md line 114]`
- **Standing bench discipline (every task):** verify `controller:` identity per port (ACM numbers shuffle across replug), live R1/R2 readback, record port / shield-rev / firmware-commit. Never trust N=1. `[VERIFIED: REQUIREMENTS.md line 7; MEMORY.md feedback_verify_port_identity_each_task]`
- **Operator adjusts the VPP pot himself.** State the target, ask him to say "done", then take ONE confirmation read. No live monitor loops. `[VERIFIED: MEMORY.md feedback_operator_adjusts_pot_solo]`
- **Leonardo is chip-out-before-sideload EXEMPT** (only Uno-class boards need chip-out). No firmware reflash is expected in Phase 99 (fix already committed in Phase 98), but if one occurs, Leonardo does not require chip removal. `[VERIFIED: MEMORY.md feedback_chip_out_before_sideload]`
- **Gitlinks stay PINNED at b10** (a1953c2 / 98b3a92) unless the operator explicitly authorizes a bump. Lockstep beta cut / stable promotion is operator-gated and OUT OF SCOPE for this milestone. `[VERIFIED: STATE.md line 73; REQUIREMENTS.md line 55]`

### Claude's Discretion (this phase)

- The exact wording of the ledger `0x08` disposition string (PASS-with-evidence-citation vs. re-named FUT) — driven by the actual bench outcome.
- Whether to extend `check_ledger.py` schema vs. add a distinct new status enum value to admit a v1.18-native `0x08` graduation (see §Ledger Update — Schema Tension). Both are valid; recommend the minimal, tested change.
- The v1.18 evidence directory layout (mirror the v1.16 `bench/<CHIP>-<op>/SHA256SUMS.txt` convention or the v1.18 `EVIDENCE.{json,md}` cell convention — recommend reusing the Phase-97 v1.18 cell schema for continuity).

### Deferred Ideas (OUT OF SCOPE)

- Re-architecting the EPROM handler/primitives. `[VERIFIED: REQUIREMENTS.md line 53]`
- The 2516 `0x0B` defect (FUT-03) and all other FUT chips. Single-chip focus. `[VERIFIED: REQUIREMENTS.md line 54]`
- Lockstep beta cut / stable promotion / gitlink reconciliation. `[VERIFIED: REQUIREMENTS.md line 55]`
- Any PCB / control-register change for a dedicated PGM strobe. `[VERIFIED: REQUIREMENTS.md line 56]`
- Bench-verifying the other 87 chips reassigned to `DIP32_27C020` (only AM27C020 is datasheet-verified; blast radius accepted as-designed, explicitly a Phase-99/future-bench residual per 98-VERIFICATION.md observation 2). Phase 99 graduates AM27C020 only. `[VERIFIED: 98-VERIFICATION.md line 91]`

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Seat chip / set VPP pot / DMM at pin 1 / confirm silkscreen | **Operator (physical bench)** | — | Irreducibly physical; no code substitute. Operator owns the pot (no monitor loops). |
| `controller:` identity + port + R1/R2 readback | **Host CLI** (`firestarter fw`, `firestarter config`/`hw`) | Operator (authorizes, confirms silkscreen) | Host queries firmware; operator confirms the Rev-2.0 silkscreen (EEPROM byte can't distinguish revs). |
| VPP rail reading at program window | **Operator (DMM)** | Host (`firestarter vpp`/`vpe` ADC monitor; `hold_rail.py` proxy) | Held-rail DMM proxy is tooling-blocked (DTR-reset-on-close); ADC monitor is the fallback measure-only path. |
| Write / verify / read-back the AM27C020 | **Host CLI** (`firestarter write -b`, `verify`, `read`) | Firmware (`configure_eprom` 0x08 dispatch) | Host orchestrates over serial; operator authorizes each live spend. |
| SHA compute + image generation | **Host / executor** (`sha256sum`, `tools/gen_test_image.py`, `hashlib`) | — | Fully scriptable; no hardware. |
| EVIDENCE.json / EVIDENCE.md authoring | **Executor** (from operator-reported readings) | — | Executor writes files; values come from operator + host output. Never fabricate. |
| PROTOCOL-LEDGER `0x08` update + `check_ledger.py` | **Executor** (edit `.md` + `.json`, run gate) | — | Pure file + script work; deterministic. |
| Extend gate to admit `0x08` graduation | **Executor** (`check_ledger.py` + `test_check_ledger.py`) | — | Software change; must keep the existing 11 rows green. |

---

## Standard Stack

No new external packages. This phase uses the existing, already-installed toolchain.

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| `firestarter` host CLI | 3.0.0b10 (installed at `~/.local/bin/firestarter`) | write / verify / read / vpp / vpe / fw / dev consistency-check on the seated chip | The project's own host CLI; the only supported way to drive the RURP shield. `[VERIFIED: firestarter --version]` |
| firmware submodule | tip `35706c2` (Phase 98-05 HEAD; reports `3.0.0b10`) | the corrected `0x08` write path under test | Fix committed in Phase 98; Phase 99 tests THIS build. Record the **submodule commit**, not the version string (version-string-caveat precedent). `[VERIFIED: git log firestarter]` |
| `python3` (3.12 devcontainer) | 3.12.13 | run `check_ledger.py`, `gen_test_image.py`, SHA compares | Already present. Note py3.12-masks-CI-3.11 trap does NOT apply here (no ruff/codegen touched unless the gate script changes — then re-run ruff on it). `[VERIFIED: repo]` |
| `sha256sum` / `hashlib` | coreutils / stdlib | byte-exact SHA comparison of written image vs read-back | The graduation oracle. `[VERIFIED: existing bench artifacts use SHA256SUMS.txt]` |

### Supporting
| Tool | Purpose | When to Use |
|------|---------|-------------|
| `tools/gen_test_image.py <size> <seed> <out>` | deterministic test image (seed 1 = image A, seed 2 = image B) | Generate the write payload. AM27C020 size = **262144** bytes. `[VERIFIED: tools/gen_test_image.py; MEMORY reference]` |
| `.planning/v1.18/bench/hold_rail.py` | hold the VPP/VPE rail open for a DMM reading without DTR-reset dropping it | If a held-rail DMM reading is attempted (tooling-blocked in Phase 97; may still be blocked). `[VERIFIED: file exists; debug/resolved/held-rail-dev-reg-timeout.md]` |
| `.planning/v1.16/ledger/tools/check_ledger.py` | ledger self-consistency gate (exit 0 = OK, 1 = structural BLOCK, 2 = infra error) | Run after every ledger edit; "0 contradictions" = exit 0. `[VERIFIED: ran it — PASS, exit 0]` |
| `.planning/v1.16/ledger/tools/test_check_ledger.py` | unit tests for the gate | Must stay green if the gate is extended for the `0x08` graduation. `[VERIFIED: file exists]` |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Manual `write -b` → `verify` → SHA | `firestarter dev write-cycle` | **REJECTED for AM27C020.** `write_cycle_eprom` erases at the start of every cycle (`eprom_operations.py:915`); a UV EPROM has no electrical erase → `erase_eprom` returns False → verdict 2 (hw-error). The passing chips (W29C020/SST39SF040/W27C512) are electrically-erasable; AM27C020 is not. Use the manual path. |
| Manual `write -b` → `verify` → SHA | `firestarter dev consistency-check` (read-only N≥3) | `consistency-check` is the READ oracle only (no write); use it for the pre-write read baseline and post-write read-back stability, NOT as the write graduation. |
| Held-rail DMM at pin 1 | `firestarter vpp` ADC monitor (measure-only) | DMM at socket pin 1 is the decisive routing measurement but was tooling-blocked in Phase 97 (DTR-reset-on-close). ADC monitor is the fallback; the routing question was already answered by code-decode (H2 disproven). |

**Installation:** none — `firestarter` is installed (`~/.local/bin/firestarter`, 3.0.0b10). If the executor's shell lacks it: `cd firestarter_app && pip install -e '.[test]'` (per MEMORY reference_firestarter_app_python_test_env; use `/usr/local` python).

---

## Package Legitimacy Audit

**Not applicable.** Phase 99 installs no external packages. All tooling (`firestarter` CLI, `check_ledger.py`, `gen_test_image.py`, `sha256sum`, `python3`) already exists in-repo or is installed. No npm/PyPI/crates dependency is introduced.

---

## Architecture Patterns

### System Architecture Diagram — Phase 99 data flow

```
                          ┌─────────────────────────────────────────────┐
                          │  PRE-01 writability result (from Phase 97)    │
                          │  = INDETERMINATE pre-fix (0-flip ≠ OTP)       │
                          └───────────────────────┬─────────────────────┘
                                                  │
              ┌───────────────────────────────────┴──────────────────────────────┐
              │  BENCH GATE (this phase): re-attempt write on the FIXED path        │
              │  operator-witnessed, Leonardo + Rev 2.0, controller-verified        │
              └───────────────────────────────────┬──────────────────────────────┘
                                                  │
   operator seats chip ──► host: firestarter fw (controller id) ──► host: config/hw (R1/R2, rev)
        │                                                                    │
        ▼                                                                    ▼
   operator sets VPP pot to 12.75V±0.25 ──► ONE confirmation read (vpp/vpe ADC + DMM if unblocked)
        │
        ▼
   executor: gen_test_image.py 262144 <seed> imgA.bin  (compute imgA SHA)
        │
        ▼
   host: firestarter write AM27C020 imgA.bin -b   ◄── operator authorizes spend
        │        (-b: skip blank-check; chip NOT-BLANK; NO --skip-erase — no erase path anyway;
        │         NO --force — SAFE-01)
        ▼
   host: firestarter read AM27C020 readback.bin   (or verify AM27C020 imgA.bin)
        │
        ▼
   executor: sha256(readback) == sha256(imgA) ?
        │
        ├── YES ──► BENCH-01 GRADUATE ──► EVIDENCE cell (fixed signature, VPP, discipline row)
        │                                     │
        │                                     ▼
        │                            LEDGER 0x08: open-defect-carried → PASS (+ gate extension)
        │                                     │
        │                                     ▼
        │                            FUT-06 RETIRED ; check_ledger.py exit 0
        │
        └── NO / 0-bits / chip proves OTP-dead ──► BENCH-01 DEFER (clean, documented)
                                              │
                                              ▼
                                     EVIDENCE cell (failing-vs-fixed signature, writability-fail)
                                              │
                                              ▼
                                     LEDGER 0x08: re-recorded residual-defect / renamed FUT
                                              │
                                              ▼
                                     FUT-06 RENAMED (e.g. software-fixed-bench-deferred)
                                              │
                                              ▼
                                     check_ledger.py exit 0 (status_changed discipline honored)
```

### Recommended artifact structure
```
.planning/v1.18/bench/
├── EVIDENCE.json          # EXTEND: add/overwrite the AM27C020 cell with the Phase-99 graduation-or-defer result
├── EVIDENCE.md            # human-readable mirror
├── check_*.py             # existing Phase-97 gates (keep green)
└── AM27C020-graduation/   # NEW: SHA256SUMS.txt + imgA.bin + readback.bin (mirror v1.16 bench/ convention)
    └── SHA256SUMS.txt

.planning/v1.16/ledger/
├── PROTOCOL-LEDGER.md     # EDIT: 0x08 row + Open Defects FUT-06 block
├── PROTOCOL-LEDGER.json   # EDIT: 0x08 row (verification_status, oracle, on_hand_chip, evidence, defect_ref) + open_defects[FUT-06]
└── tools/
    ├── check_ledger.py    # EXTEND: admit a v1.18-native 0x08 PASS (see Schema Tension)
    └── test_check_ledger.py  # EXTEND: cover the new 0x08 path; keep existing tests green
```

### Pattern 1: Manual write→verify graduation for a non-erasable UV EPROM
**What:** Because `dev write-cycle` erases first (fatal on a UV EPROM), graduate via the manual sequence, exactly the shape Phase 97 used to capture the failure signature.
**When to use:** Any UV EPROM without `FLAG_CAN_ERASE` (AM27C020, 2516, ST M27C512, etc.).
**Example:**
```bash
# Source: firestarter_app/firestarter/cli_handlers.py:444-511 (write), 514-543 (verify);
#         eprom_operations.py:875-960 (write_cycle erases — do NOT use here)
# 1. Generate deterministic image (AM27C020 = 262144 bytes)
python3 firestarter_app/tools/gen_test_image.py 262144 1 /tmp/am27c020_imgA.bin
sha256sum /tmp/am27c020_imgA.bin                         # record image SHA

# 2. Write (operator-authorized). -b skips ONLY blank-check (chip is NOT-BLANK, 0x02@0x0000).
#    NO --skip-erase (there is no erase for a UV EPROM anyway), NO --force (SAFE-01).
firestarter write AM27C020 /tmp/am27c020_imgA.bin -b

# 3. Read back and compare independently (host-side SHA compare = the graduation oracle)
firestarter read AM27C020 /tmp/am27c020_readback.bin
sha256sum /tmp/am27c020_readback.bin                     # == imgA SHA  ⇒ GRADUATE
#   OR: firestarter verify AM27C020 /tmp/am27c020_imgA.bin   (RC=0 ⇒ byte-exact)

# 4. Stability (do not trust N=1): read the programmed chip N≥3, expect 1 distinct SHA
firestarter dev consistency-check AM27C020 --runs 3
```
**Note on `-b` and SAFE-01 (verified in Phase 97):** for a UV EPROM (no `FLAG_CAN_ERASE`), `-b` skips only the blank-check; the over-voltage guard (`vpp_check_window`) keys on `FLAG_FORCE`, not `FLAG_SKIP_BLANK_CHECK`, so SAFE-01 is fully intact. `[VERIFIED: 97-VERIFICATION.md line 92, 140]`

### Pattern 2: 1→0 program proof
**What:** A UV EPROM programs bits 1→0 only. The proof of a working program pulse is that a known-1 bit region drops to 0 and reads back stable. The failing signature (pre-fix) was bad-bytes 1/1, retries 20, `bits_flipped=0`, pre==post SHA (chip pristine). The graduation signature is the inverse: the written image's 0-bits are present in the read-back and the SHA matches.
**When to use:** BENCH-02 evidence — record either the graduated signature (fixed) or, if the write still fails, the failing-vs-fixed differential (0-bits again) as the deferral evidence.
**Example (the Phase-97 failing baseline to differentiate against):**
```
# Source: .planning/v1.18/bench/EVIDENCE.json cell AM27C020 (pre-fix)
bad_bytes: 1/1 ; retries: 20 ; bits_flipped: 0 ; vpp_adc_mv: 13000
pre_read_sha256 == post_read_sha256 (90cd45f5…) ⇒ chip pristine, 0-bits programmed
```

### Anti-Patterns to Avoid
- **Using `dev write-cycle` on AM27C020.** It erases first → verdict 2 (hw-error), not a real graduation. Use the manual `write -b` path.
- **Passing `--force`.** Bypasses the chip-ID and VPP guards → violates SAFE-01. Never.
- **Recording a v1.18 `0x08` PASS with `p90_*_sha_matches_v115: true`.** There is no v1.15 write baseline for AM27C020 — that flag would be a fabricated claim. Extend the gate honestly instead (§Schema Tension).
- **Flipping `open_defects[FUT-06].status_changed` to `true` casually.** The gate asserts every `open_defects[].status_changed is False` (`_assert_ledger03` c). To graduate, the FUT-06 defect must be *removed from / retired out of* `open_defects` (not left in with `status_changed: true`), OR the retirement modeled so the assertion still holds. Plan the exact JSON shape.
- **Trusting N=1.** Standing discipline; take N≥3 stable reads before declaring PASS.
- **Fabricating a DMM value.** If the held-rail DMM is still tooling-blocked, record "not measured" with the reason (as Phase 97 did) — never invent a number.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Deterministic write payload | ad-hoc `dd if=/dev/urandom` | `tools/gen_test_image.py <size> <seed>` | Byte-stable across hosts; seed 1/2 = image A/B convention already used by every prior bench; reproducible SHA. |
| Write/read/verify orchestration | raw serial JSON | `firestarter write/read/verify` | The CLI handles the INIT/MAIN/END state machine, COBS framing, CRC8, chunking, chip-ID + VPP guards. |
| Ledger consistency checking | eyeballing the tables | `check_ledger.py` (exit 0/1/2) | Machine-checked join keys, D-09 PASS constraint, status enum, defect discipline. "0 contradictions" = exit 0. |
| SHA compare | custom differ | `sha256sum` / `hashlib.sha256` + `SHA256SUMS.txt` | The established bench oracle; artifacts already use this format. |
| Read stability check | manual re-reads | `firestarter dev consistency-check --runs 3` | 3-way verdict (0/1/2), keeps per-run binaries, prints divergent offsets. |

**Key insight:** Every prior graduation in this project (v1.13/v1.15/v1.16 P90/P91) used exactly this toolchain (`gen_test_image` → write → read-back → SHA compare → `SHA256SUMS.txt` → ledger). Phase 99 should follow the same rails; the only novelties are (a) the manual write path (UV EPROM can't use `write-cycle`) and (b) the ledger-gate extension for a v1.18-native `0x08` PASS.

---

## Runtime State Inventory

> Phase 99 is a bench + documentation phase, not a rename/refactor. It does, however, mutate two canonical persisted records — inventoried here so no stale state survives.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data (ledger) | `PROTOCOL-LEDGER.json` row `0x08` (`verification_status: open-defect-carried`, `defect_ref: FUT-06`, `evidence: null`, `oracle: null`, `on_hand_chip: null`) AND `open_defects[]` FUT-06 block AND the parallel `.md` mirror | **Data edit:** update the row + defect block per outcome; keep `.md` and `.json` in lockstep (they carry the same rows). |
| Stored data (evidence) | `.planning/v1.18/bench/EVIDENCE.json` AM27C020 cell (currently the pre-fix RCA-01 failure signature) | **Data edit:** add or extend a Phase-99 post-fix cell (graduate or defer); reuse the locked column schema. Do NOT overwrite the Phase-97 RCA cell if `check_signature.py` still needs it — prefer a new cell or a clearly-versioned field. Verify `check_signature.py` / `check_pre01.py` still pass after the edit. |
| Live service config | none | None — no external service holds `0x08`/AM27C020 state. |
| OS-registered state | none | None. |
| Secrets/env vars | `FIRESTARTER_LEDGER_FILE`, `FIRESTARTER_EVIDENCE_FILE`, `FIRESTARTER_MATRIX_FILE` (env-overridable paths in `check_ledger.py`) | None — defaults resolve correctly from repo root; only relevant if the gate is run from an unusual CWD. `FIRESTARTER_CONFIG_DIR` test seam exists for host config isolation (MEMORY). |
| Build artifacts | firmware submodule tip `35706c2` is the fix-under-test; the Leonardo may or may not already carry it | **Verify (operator):** confirm the Leonardo is running the Phase-98 fix build (`firestarter fw` → record commit). If it carries an older build, a reflash is needed (Leonardo is chip-out-EXEMPT). Record the actual flashed commit in evidence. |
| Traceability | `REQUIREMENTS.md` lines 73–74 (BENCH-01/02 = Pending); `ROADMAP.md` line 241 top-level Phase-99 checkbox; `STATE.md` | **Doc edit at phase close:** flip BENCH-01/02 to Complete, check the Phase-99 box, update STATE. (Bookkeeping — also close the noted ROADMAP-98 checkbox lag from 98-VERIFICATION.md observation 1.) |

**Nothing found in category:** Live service config, OS-registered state — verified: `0x08`/AM27C020 state lives only in the two `.planning/` records above and on the physical chip.

---

## Common Pitfalls

### Pitfall 1: `dev write-cycle` erases and dies on the UV EPROM
**What goes wrong:** Reaching for `firestarter dev write-cycle` (the harness that graduated the other 3 chips) returns verdict 2 (hw-error) on AM27C020.
**Why it happens:** `write_cycle_eprom` calls `erase_eprom` at the top of every cycle (`eprom_operations.py:915`); AM27C020 is a UV EPROM with no `FLAG_CAN_ERASE`, so erase fails.
**How to avoid:** Use the manual `write -b` → `verify`/`read` → SHA sequence (Pattern 1).
**Warning signs:** "erase failed" / RC=2 on the first cycle. `[VERIFIED: eprom_operations.py:911-918]`

### Pitfall 2: The `check_ledger.py` D-09 PASS constraint has no v1.15 write baseline for 0x08 (THE central pitfall)
**What goes wrong:** Setting the `0x08` row to `verification_status: "PASS"` fails the gate, because `_assert_ledger02_d09` requires `evidence.p90_read_sha_matches_v115 == true` AND `evidence.p90_writecycle_sha_matches_v115 == true`, and there is no v1.15 write-cycle baseline (v1.15 write was the 0-bits failure). Forcing those flags to `true` would be a fabricated claim.
**Why it happens:** The gate was authored in v1.16 to prove "recompose didn't regress vs. the v1.15 baseline." AM27C020 never had a passing v1.15 write baseline — v1.18 is its *first* successful write, a *v1.18-native graduation*, not a regression check.
**How to avoid:** Extend `check_ledger.py` (and `test_check_ledger.py`) to admit a v1.18-native `0x08` PASS whose evidence is self-consistency (written-image SHA == read-back SHA on this milestone's fixed firmware) rather than "matches v1.15". Options: (a) a new evidence shape (`v1_18_writeverify_sha_selfconsistent: true` + oracle + artifacts) recognized for the `0x08` row; (b) a distinct new status enum (e.g. `PASS-v1.18-native`) added to `_VALID_STATUSES` with its own constraint. Recommend the minimal, well-tested change; keep all 11 existing rows green. **This is a required, first-class plan task.**
**Warning signs:** `check_ledger.py` exit 1 with `LEDGER-02/D-09: PASS row bucket=0x08 evidence.p90_writecycle_sha_matches_v115 is not true`. `[VERIFIED: check_ledger.py:140-179; live gate run + v1.15 EVIDENCE.json AM27C020 cell = read-only PASS, write FAILED]`

### Pitfall 3: FUT-06 retirement vs. the `status_changed is False` invariant
**What goes wrong:** Leaving FUT-06 in `open_defects[]` with `status_changed: true` trips `_assert_ledger03` (which requires every `status_changed is False`) → gate exit 1.
**Why it happens:** The gate deliberately forbids silently mutating a carried defect's status.
**How to avoid:** To *retire* FUT-06 on graduation, **remove** it from `open_defects[]` (its resolution now lives in the graduated `0x08` row's evidence + citation), rather than flipping its flag. To *re-record* it on deferral, keep the block but update its `disposition` string and keep `status_changed: false` (its status is carried, re-described, not "changed" in the gate's sense) — OR rename it to a new FUT id. Decide the exact JSON shape in the plan and unit-test it.
**Warning signs:** `LEDGER-03: open_defect id='FUT-06' status_changed is not false`. `[VERIFIED: check_ledger.py:207-214]`

### Pitfall 4: D-04 no-copy SHA guard rejects raw 64-hex strings in the ledger
**What goes wrong:** Pasting the graduation SHA-256 directly into `PROTOCOL-LEDGER.json` fails the gate — `_assert_ledger01` (d) rejects any raw 64-hex string anywhere in the serialized ledger.
**Why it happens:** D-04 compose-by-cross-reference: SHA digests stay authoritative in the upstream evidence files (`EVIDENCE.json`, `SHA256SUMS.txt`), not copied into the ledger.
**How to avoid:** In the ledger, reference the evidence by *artifact path + join key* (e.g. `evidence_chip: "AM27C020"`, `p90_artifacts: [".planning/v1.18/bench/AM27C020-graduation/"]`), never the raw SHA. Put the SHA in `EVIDENCE.json` / `SHA256SUMS.txt`.
**Warning signs:** `LEDGER-01 (D-04): raw 64-hex SHA string(s) found in ledger`. `[VERIFIED: check_ledger.py:59-60, 129-137]`

### Pitfall 5: Held-rail DMM at pin 1 is tooling-blocked
**What goes wrong:** Attempting `firestarter dev reg 0 0 0x86 -f` (or via `timeout`) to hold the rail for a DMM read drops the Leonardo when the port closes (DTR-reset-on-close), so the reading is lost.
**Why it happens:** The `finally: _disconnect` in the CLI resets the Leonardo; the rail collapses.
**How to avoid:** Use `hold_rail.py` (keeps the port open) if a DMM reading is attempted. If still blocked, record "not measured — held-rail proxy blocked (DTR-reset-on-close)" with the debug-doc reference and rely on the `vpp`/`vpe` ADC monitor + the Phase-97 code-decode (H2 disproven, VPP routes to pin 1). Never fabricate. `[VERIFIED: 97-VERIFICATION.md gap 1; MEMORY reference_held_rail_dtr_reset_hold_script; debug/resolved/held-rail-dev-reg-timeout.md]`

### Pitfall 6: VPP target confusion (12.75V band, not 13.0V; and vpp ≠ vpe rail)
**What goes wrong:** Setting VPP to the wrong level, or reading the wrong rail. AM27C020 datasheet VPP = **12.75V ±0.25** (DB ships `vpp_mv=13000`, top of band). Phase 97 as-found VPP was 12.0V (below band) → operator raised to 13.0V before the attempt.
**Why it happens:** `firestarter vpp` and `firestarter vpe` are *different* continuous monitors; the `0x08` program path uses the P1-VPP routing (pin 1). The ~15-19V `vpp` reading in some contexts is the dropped 0x07/0x08 path, not the program rail (MEMORY project_phase79_gate_reexamined nuance).
**How to avoid:** State the target (12.75V±0.25, i.e. ~12.75–13.0V) to the operator, have him set the pot and say "done", then take ONE confirmation read via `firestarter vpp`. Record the confirmed value. `[VERIFIED: REQUIREMENTS.md line 9; EVIDENCE.json anomalies; MEMORY]`

---

## Code Examples

### VPP / VPE monitor sample (measure-only, capture one reading)
```bash
# Source: cli_handlers.py:659-680 (vpp/vpe); MEMORY reference_v114_bench_erase_rail_and_test_artifact
# vpp/vpe are CONTINUOUS monitors — capture a sample with timeout+SIGINT, line-buffered:
timeout -s INT 15 stdbuf -oL firestarter vpp   # VPP rail sample during the confirmation window
timeout -s INT 15 stdbuf -oL firestarter vpe   # VPE (program) rail sample
```

### Controller identity + hardware readback (bench-discipline row)
```bash
# Source: cli_handlers.py:769 (fw), 688-694 (hw), 697 (config)
firestarter fw       # controller identity + firmware version/commit — record BEFORE any op, per port
firestarter hw       # hardware revision (EEPROM byte; silkscreen is the authoritative oracle)
firestarter config   # R1/R2 calibration readback (record R1≈270000, R2≈44000 per prior sessions)
```

### Ledger gate invocation ("0 contradictions" = exit 0)
```bash
# Source: check_ledger.py:221-269 ; ran live 2026-07-01 → PASS exit 0
cd /workspaces
python3 .planning/v1.16/ledger/tools/check_ledger.py ; echo "exit=$?"
# exit 0 = OK (0 contradictions) ; 1 = structural BLOCK ; 2 = infra error (missing/malformed input)
# Also run the gate's own unit tests after any gate change:
cd /workspaces/.planning/v1.16/ledger/tools && python3 -m pytest test_check_ledger.py -q
```

### SHA artifact convention (mirror v1.16 bench/)
```bash
# Source: .planning/v1.16/ledger/bench/W27C512-fix/SHA256SUMS.txt (annotated header + sums)
mkdir -p .planning/v1.18/bench/AM27C020-graduation
sha256sum /tmp/am27c020_imgA.bin /tmp/am27c020_readback.bin \
  > .planning/v1.18/bench/AM27C020-graduation/SHA256SUMS.txt
# Prepend a comment header: firmware commit, controller, shield, method, verdict.
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `0x08` = `open-defect-carried (FUT-06)`, 0-bits programmed, RC-1 = pin 31 modeled as A18 | Fixed: `DIP32_27C020` pinout `rw-pin:[31]` → `CTRL_READ_WRITE` (0x40, revision-invariant); pin 31 held as /PGM control not address line | Phase 98 (2026-07-01) | Phase 99 is the empirical test of this fix; 119/119 native + golden traces byte-identical, but silicon behavior unproven until now. |
| `-b` implied skip-erase | Phase 92 decouple: `-b` skips ONLY blank-check; `--skip-erase` is separate | v1.16 Phase 92 | For a UV EPROM (no erase path) `-b` is exactly right and safe; no `--skip-erase` needed. |
| `write -b` on erasable chips silently corrupts (skips erase) | plain `write` for erasable NOR/EEPROM; `-b` only for genuinely-blank or non-erasable UV | v1.16 P91 RCA | Does NOT affect AM27C020 (UV, no erase) — `-b` remains correct here. |

**Deprecated/outdated:**
- The pre-fix `DIP32_STD` pin-31=A18 mapping for ≤256K 0x08 chips — superseded by `DIP32_27C020` (Phase 98). AM27C040/AM27C080 (>256K) correctly stay on `DIP32_STD` (size-gated).

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The seated AM27C020 remains writable/OTP-indeterminate as of Phase 99 (Phase 97 left it pristine, 0-bits, INDETERMINATE). | Decision Structure | If the chip is now definitively OTP/dead, BENCH-01 takes the deferral branch — which the plan must fully support anyway. Low risk (plan covers both branches). |
| A2 | The Leonardo currently carries (or will be reflashed to) the Phase-98 fix build (submodule `35706c2`). | Runtime State Inventory | If it carries an older build, the write will still fail 0-bits and the "graduation" would be invalid. Mitigate: operator confirms `firestarter fw` commit before any spend (bench-discipline task). |
| A3 | AM27C020 VPP target is 12.75V±0.25 (DB `vpp_mv=13000`). | Pitfall 6 | Wrong VPP under-programs or over-stresses. Sourced from REQUIREMENTS.md line 9 (research brief) — treat as project-locked, but operator confirms the pot reading. |
| A4 | Extending `check_ledger.py` to admit a v1.18-native `0x08` PASS is acceptable (the gate is a project-owned tool, not a frozen contract). | Schema Tension | If the operator/planner prefers to leave `0x08` at a documented FUT status instead of PASS even on a successful write, the gate extension may be unnecessary. Surface as an open question. |
| A5 | R1≈270000 / R2≈44000 are the expected calibration readbacks (from prior sessions). | Code Examples | Only affects the recorded discipline row; operator readback is authoritative. |

**These `[ASSUMED]` items should be confirmed at the Phase-99 discuss/plan step or by the operator at the bench before the graduation spend.**

---

## Open Questions

1. **On a successful write, is the target ledger status `PASS` (requiring the gate extension) or a documented `supported`-with-evidence FUT closure?**
   - What we know: ROADMAP SC#3 says "updated … to PASS (if graduated) or a documented residual-defect / FUT status (if deferred)."
   - What's unclear: whether "PASS" is mandatory on graduation, and thus whether the `check_ledger.py` D-09 extension is in-scope for Phase 99 or a follow-up.
   - Recommendation: treat the gate extension as in-scope (a graduated chip *should* read PASS in the canonical ledger, and the gate must pass at 0 contradictions per SC#3). Confirm at plan-check.

2. **FUT-06 retirement mechanism: remove from `open_defects[]` vs. rename to a new FUT?**
   - What we know: on graduation FUT-06 is "retired"; the gate forbids `status_changed: true`.
   - What's unclear: the exact desired JSON shape (delete the block vs. move to a "resolved defects" record).
   - Recommendation: on PASS, remove FUT-06 from `open_defects[]` and cite the graduated `0x08` row's evidence; on defer, keep + re-describe (status_changed stays false) or rename. Decide in the plan; unit-test either way.

3. **Is a held-rail DMM reading at socket pin 1 achievable this session, or still tooling-blocked?**
   - What we know: Phase 97 was blocked (DTR-reset-on-close); `hold_rail.py` was delivered as the workaround.
   - What's unclear: whether `hold_rail.py` reliably holds the rail long enough for a DMM read on this bench.
   - Recommendation: attempt `hold_rail.py`; if still blocked, record "not measured" with reason and lean on the `vpp` ADC monitor + code-decode routing proof (Phase 97 precedent). Never fabricate.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `firestarter` host CLI | BENCH-01/02 write/verify/read/vpp | ✓ | 3.0.0b10 (`~/.local/bin/firestarter`) | `pip install -e '.[test]'` in `firestarter_app/` |
| `python3` | check_ledger.py, gen_test_image.py | ✓ | 3.12.13 | — |
| `sha256sum` | SHA compare | ✓ | coreutils | `python3 -c "import hashlib…"` |
| `check_ledger.py` | ledger gate | ✓ (runs, exit 0 today) | in-repo | — |
| `gen_test_image.py` | write payload | ✓ | in-repo (`firestarter_app/tools/`) | — |
| `hold_rail.py` | held-rail DMM proxy | ✓ (may be functionally blocked) | in-repo (`.planning/v1.18/bench/`) | `vpp`/`vpe` ADC monitor + code-decode |
| **Leonardo + RURP Rev 2.0 + seated AM27C020** | ALL bench ops | **operator-provided (not verifiable from devcontainer)** | Rev 2.0 (silkscreen) | **none — blocks BENCH-01/02 until operator is at the bench** |
| DMM at socket pin 1 | ideal VPP routing measurement | operator-provided | — | ADC monitor (`vpp`), code-decode (H2 disproven) |

**Missing dependencies with no fallback:**
- Physical bench hardware (Leonardo + Rev 2.0 + seated AM27C020 + operator). BENCH-01/02 cannot proceed without an operator-authorized bench session. All software prep (image gen, gate extension, evidence/ledger scaffolding) can be done ahead of time; the *live spend* and *readings* gate the phase.

**Missing dependencies with fallback:**
- Held-rail DMM → `vpp`/`vpe` ADC monitor + Phase-97 code-decode routing proof.

---

## Validation Architecture

> `workflow.nyquist_validation` is not present in `.planning/config.json` → treated as enabled. However, Phase 99's "validation" is primarily an operator-witnessed hardware gate, not an automated test suite. The automatable validation is the ledger gate + its unit tests.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (host: `firestarter_app`) + `check_ledger.py`/`check_*.py` standalone gate scripts |
| Config file | `firestarter_app/pyproject.toml` (host); gate scripts are argv-free standalone |
| Quick run command | `python3 .planning/v1.16/ledger/tools/check_ledger.py` |
| Full suite command | `cd .planning/v1.16/ledger/tools && python3 -m pytest test_check_ledger.py -q` + Phase-97 gates (`check_pre01/signature/diff07/verdict.py`) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| BENCH-01 | write→verify byte-exact OR clean deferral | manual-only (hardware) | `firestarter write -b` → `verify`/`read` → `sha256sum` compare | ✅ CLI exists; result is operator-witnessed |
| BENCH-01 | read stability (not N=1) | manual-only (hardware) | `firestarter dev consistency-check AM27C020 --runs 3` | ✅ |
| BENCH-02 | EVIDENCE cell complete + consistent | automated | `python3 .planning/v1.18/bench/check_signature.py` (extend/reuse for the P99 cell) | ✅ (Phase-97 gate; may need a P99 sibling) |
| LEDGER (SC#3) | ledger self-consistent at 0 contradictions | automated | `python3 .planning/v1.16/ledger/tools/check_ledger.py` (exit 0) | ✅ |
| LEDGER (SC#3) | gate change doesn't regress the 11 other rows | automated | `python3 -m pytest test_check_ledger.py -q` | ✅ (must extend) |

### Sampling Rate
- **Per task commit:** `check_ledger.py` (after any ledger edit); `pytest test_check_ledger.py` (after any gate edit).
- **Per wave merge:** full gate-script set (Phase-97 checks + check_ledger) green.
- **Phase gate:** `check_ledger.py` exit 0 + BENCH-01/02 evidence complete + operator sign-off before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `check_ledger.py` / `test_check_ledger.py` — extend for a v1.18-native `0x08` PASS (or new status) WITHOUT a v1.15 write baseline; keep the 11 existing rows green. (The single required software task.)
- [ ] A Phase-99 EVIDENCE gate (reuse `check_signature.py` shape or add a `check_graduation.py`) to assert the P99 cell fields are filled + SHA-self-consistent (no fabrication). Optional but recommended.
- *(No test-framework install needed — pytest + gate scripts already present.)*

---

## Security Domain

> `security_enforcement` is not set in `.planning/config.json`. This phase is firmware-safety-adjacent (over-voltage on a UV EPROM) rather than a networked/authn system, so the relevant "security" surface is the electrical-safety invariant (SAFE-01), not ASVS web categories.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — (no auth surface) |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | partial | The ledger/evidence JSON edits must remain schema-valid — enforced by `check_ledger.py` + the check scripts (they ARE the input-validation gate). |
| V6 Cryptography | partial | SHA-256 is used as an integrity/identity oracle, not for confidentiality. Use `sha256sum`/`hashlib` — never hand-roll. |

### Known Threat Patterns for this bench/ledger phase (project-specific safety, STRIDE-framed)

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Over-voltage on socket pin 1 damages the chip | (safety) Denial/Destruction | SAFE-01: firmware `vpp_check_window` ERROR-blocks over-voltage (keys on `FLAG_FORCE`); never pass `--force`; VPP target 12.75V±0.25 confirmed before spend. |
| Fabricated graduation evidence (faked SHA/DMM) | Tampering / Repudiation | Independent host-side SHA compare; N≥3 stability; "not measured" recorded honestly when tooling-blocked; operator-witnessed; D-04 no-copy guard keeps SHAs in the authoritative evidence file. |
| Ledger status silently changed (defect hidden) | Repudiation | `check_ledger.py` `status_changed is False` invariant + status enum + D-09 PASS constraint; the gate is the tamper-evidence mechanism. |
| Wrong firmware build tested (stale, un-fixed) | Spoofing (of "the fix") | Record the firmware submodule commit (not the version string, which doesn't distinguish builds); operator confirms `firestarter fw` before the spend. |

---

## Sources

### Primary (HIGH confidence)
- `.planning/REQUIREMENTS.md` — BENCH-01/02 exact text, constraints, PRE-01 gate, FUT-06, SAFE invariant, VPP=12.75V±0.25. (read in full)
- `.planning/ROADMAP.md` lines 241, 302–314 — Phase-99 goal, depends-on, success criteria.
- `.planning/v1.16/ledger/PROTOCOL-LEDGER.{md,json}` — current `0x08` row (`open-defect-carried`, FUT-06), status enum key, Open Defects blocks. (read in full)
- `.planning/v1.16/ledger/tools/check_ledger.py` — D-09 PASS constraint, D-04 no-copy guard, status-enum, `status_changed` invariant, exit-code contract. (read in full; ran live → PASS exit 0)
- `.planning/v1.18/bench/EVIDENCE.json` + `check_signature.py` — Phase-97 cell schema (locked_columns), pre-fix AM27C020 failure signature, W27C512 differential control.
- `.planning/v1.15/bench/EVIDENCE.json` (AM27C020 cell) — confirms a v1.15 *read* PASS but *write* FAILURE (no write baseline) — the D-09 tension root cause.
- `firestarter_app/firestarter/cli_handlers.py` — `write` (444–511), `verify` (514–543), `vpp`/`vpe` (659–680), `hw`/`config` (688–697), `fw` (771), `dev consistency-check` (1082–1169), `dev write-cycle` (1172+).
- `firestarter_app/firestarter/eprom_operations.py` — `consistency_check_eprom` (671+), `write_cycle_eprom` erases first (875–960) → unusable on UV EPROM.
- `.planning/phases/97-*/97-VERIFICATION.md` + `98-*/98-VERIFICATION.md` — PRE-01 INDETERMINATE result, RC-1 confirmation, the corrected `CTRL_READ_WRITE` fix, "Phase 99 sole empirical gate."
- `.planning/STATE.md` — deferred items (FUT-06 ACTIVE), v1.18 research findings, decisions log.

### Secondary (MEDIUM confidence)
- `.planning/v1.16/ledger/bench/W27C512-fix/SHA256SUMS.txt` + `BENCH-LOG.md` — the SHA-artifact convention + prior graduation method (gen_test_image → write → read-back → SHA).
- Global MEMORY.md notes: operator-adjusts-pot, held-rail DTR-reset, VPP/VPE monitor semantics, chip-out-before-sideload (Leonardo exempt), verify-port-identity, v1.18 Phase 97/98 closeouts.

### Tertiary (LOW confidence)
- None. No WebSearch/external sources were needed; this is an internal-artifact phase.

---

## Metadata

**Confidence breakdown:**
- Standard stack / host commands: HIGH — read directly from `cli_handlers.py` + `eprom_operations.py`; `firestarter --version` confirmed installed.
- Ledger gate + schema tension: HIGH — `check_ledger.py` read in full, ran live (exit 0), and the v1.15 AM27C020 cell inspected to confirm no write baseline.
- Decision structure (graduate vs defer): HIGH — ROADMAP SC + REQUIREMENTS PRE-01 language explicit; both branches documented.
- Operator-vs-automated split: HIGH — grounded in standing MEMORY discipline + Phase-97 precedent.
- Exact VPP pot value / current chip writability: MEDIUM (A1/A3) — project-locked but operator-confirmed at bench.

**Research date:** 2026-07-01
**Valid until:** 2026-07-31 (stable internal artifacts; the only volatility is the physical bench outcome, resolved at execution).
