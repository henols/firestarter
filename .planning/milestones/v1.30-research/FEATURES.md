# Feature Research

**Domain:** Host CLI surface retirement + behavioral (inverted-assertion) test leg for an unreadable hardware state
**Milestone:** v1.30 SDP Surface Retirement & Behavioral Lock Proof (host-only, `firestarter_app`)
**Researched:** 2026-08-03
**Live tree verified against:** `firestarter_app` branch `beta` @ `16a313a`
**Confidence:** HIGH on the host-surface mechanics (all measured against the live tree); LOW on the external competitor comparison (web-sourced); the *causal* silicon claim is out of reach by design (see Evidence Ceiling).

---

## 0. Verification of every inherited file:line claim

The design note and `PROJECT.md` carry line references written at different times. Verified individually:

| Claim (source) | Status |
|---|---|
| `chip_test.py:289-295` — op vocabulary | **VERIFIED.** `OP_ID`=289 … `OP_ERASE`=295, exactly seven strings |
| `chip_test.py:636` — `_DESTRUCTIVE_OPS` | **VERIFIED**, exact line |
| `chip_test.py` `derive_plan` | **VERIFIED** at `:394` |
| `chip_test.py` `_MULTI_RUN_OPS` | **VERIFIED** at `:654` (not claimed, but co-load-bearing — see §1.3) |
| Verdict vocabulary `OK/BAD/NA/SKIPPED/marginal` | **VERIFIED** at `chip_test.py:620-624` |
| `sdp_capability.py:266` — `sdp_capability()` | **VERIFIED.** Signature is `(chip_name: str, db: Any) -> tuple[bool, str]` |
| `sdp_capability` partition "43 ALLOW / 41 REFUSE of 84" | **VERIFIED BY LIVE MEASUREMENT** (not carried forward): 84 chips at `protocol-id == 0x0D`, 43 allow, 41 refuse |
| `eprom_operations.py:1736` — `sdp_unlock` | **VERIFIED**, exact line |
| `eprom_operations.py:1784` — `sdp_lock` | **VERIFIED**, exact line |
| `constants.py:72-73` — `COMMAND_SDP_UNLOCK`/`COMMAND_SDP_LOCK` | **VERIFIED** (=9 / =10); `COMMAND_NAMES` entries at `:90-91` |
| `constants.py:66` — "unconditional in firmware" comment | **VERIFIED** |
| `COMMAND_NAMES[cmd]` dereferenced at `eprom_operations.py:301` and `:377` | **STALE.** Actual dereference sites are **`:329`** and **`:405`**. The claim's *substance* holds — both are real `COMMAND_NAMES[cmd]` lookups at operation setup, so a deleted entry is a `KeyError`, not a cosmetic gap. Note `constants.py:69` repeats the stale `:301` internally; correcting that comment is free while the file is open. |
| host-side auto-unlock at `eprom_operations.py:1637` | **PARTIALLY STALE.** `:1637` lands inside the explanatory comment block; the live conditional is **`:1654`** (`if is_protocol_0x0d and (operation_flags & FLAG_SKIP_SDP_UNLOCK):`) |
| `cli_handlers.py:2095-2227` — `dev_sdp` and its four gates | **STALE.** Actual span is **`:2196` (`@dev.command(name="sdp")`) → `:2213` (`def dev_sdp`) → `:2321` (EOF)**. The command is the last thing in the file, which makes the deletion a clean tail truncation. |
| `dev_test(app, chip)` at `cli_handlers.py:1958` | **STALE.** Actual: `@dev.command(name="test")` at **`:2055`**, `def dev_test(app: "AppContext", chip: str)` at **`:2059`**. The *substance* holds — verified zero options besides `--help`. |
| `--sdp-relock` deferral label at `STATE.md:532` / `PROJECT.md:705` | Not re-verified (meta-repo bookkeeping, already corrected in `PROJECT.md`'s own note) |

**Two new findings that change the safety story — see §2.6 and §1.4.**

---

## 1. The `dev test` SDP leg — user-visible surface

### 1.1 Recommended op names

The existing vocabulary is lowercase, hyphenated, and terse, with a `write-partial` precedent for *qualified* writes. Four new strings fit that grain:

| New op | Step | Kind | In `_DESTRUCTIVE_OPS`? | In `_MULTI_RUN_OPS`? |
|---|---|---|---|---|
| `sdp-lock` | 2 — emit CMD 10 | emission-only | **YES** (mutates chip state) | **NO** (needs own single-run arm) |
| `write-inhibited` | 3 — **the oracle** | inverted assertion | **YES** | **NO** (inverted verdict logic — needs own arm) |
| `sdp-unlock` | 4a — emit CMD 9 | emission-only | **YES** | **NO** |
| `write-restored` | 4b — rewrite + read-back | writability proof | **YES** | **NO** (folds write+read-back like `write-inhibited`) |

**Step 1 (baseline write pattern A + verify) should NOT get a new op — reuse the existing `write` + `verify` steps.** Verified: `derive_plan(… write_scope="full")` on `AT28C256` already emits `write` with `write_region=(0, 256)` followed by `verify` with the same region. Adding a `sdp-baseline-write` op would duplicate an existing destructive step and double the write count for no new information. The baseline the note asks for is already there; the leg appends after `erase`.

Resulting step list for a capability-ALLOWED `0x0D` chip (verified derivation order + 4 appended):

```
id(NA) · read · blank-check · write · verify · erase(NA)
        · sdp-lock · write-inhibited · sdp-unlock · write-restored
```

**Pattern A is free and needs no storage.** `generate_pattern(start, length)` is deterministic and address-derived (`chip_test.py:59`), so step 3's oracle recomputes pattern A rather than remembering it. Measured for `AT28C256`: region `(0, 256)`, pattern A = `00 01 02 03 04 05 06 07 …`.

**Pattern B should be the bitwise complement of pattern A**, not `prepass_images`' all-`0xFF`. Measured: complement of A `[:8]` = `ff fe fd fc fb fa f9 f8` — differs from A in **every byte**, so a change at *any* offset is detectable. All-`0xFF` would coincide with A wherever `address_fold_byte == 0xFF`, creating blind offsets in the oracle.

### 1.2 What each step reports — PASS / BAD / NA-because-REFUSED

| Step | On PASS | On BAD | On NA (capability-REFUSED) |
|---|---|---|---|
| `sdp-lock` | `OK` — "lock sequence emitted (protection state is not readable on this family; this is not a claim about the chip's state)" | `BAD` + `error_code` — e.g. `MSG_ERR_UNKNOWN_CMD` ⇒ firmware predates Phase 119 | `NA` carrying `sdp_capability()`'s reason, **no operator call** |
| `write-inhibited` | `OK` — "unlock-declined write left all 256 bytes equal to pattern A — consistent with SDP inhibiting the write" | `BAD` + diff count + first offset + `classify_fingerprint` bucket | `NA`, same reason |
| `sdp-unlock` | `OK` — "unlock sequence emitted; part left unlocked" | `BAD` + recovery line (§3) | `NA`, same reason |
| `write-restored` | `OK` — "part accepted pattern A again; writability restored" | `BAD` + recovery line (§3) | `NA`, same reason |

The NA mechanism is already built: `run_plan` (`chip_test.py:780-782`) turns any `Step(supported=False)` into `_skip_result(step.op, step.reason, verdict=VERDICT_NA)` **without any operator call**. So "REFUSED chips get an NA step carrying `reason`, never a silent omission" needs zero new machinery — only `derive_plan` emitting the four steps with `supported=False`.

The 41 refusal reasons are already user-facing prose, measured live, e.g.:
> `2816: not on the SDP-capable list: 2816 (pre-SDP generation). Refused fail-closed because the SDP command sequence is not inert on a part without an SDP command decoder — its bytes are stored as data at the bus-truncated magic addresses.`

These are long, but they do **not** bloat the `rich` table: `DiagnosticReport.render()` (`diagnostic_report.py:471-476`) renders only `op`, `verdict`, `error_code`, `fingerprint` per step — `reason` appears only in the markdown table and the JSON block.

### 1.3 Consumers of `StepResult.op` — the D-06/D-07 claim re-verified

**The claim holds, and is stronger than stated: no production consumer anywhere in the tree hard-codes an op string.** Measured:

| Consumer | Reads | Needs a change? |
|---|---|---|
| `diagnostic_report._step_dict` `:408` | `result.op` generically | **No** |
| `diagnostic_report.dedup_fingerprint` `:224` | `f"{result.op}={result.verdict}:{cls}"` | **No** |
| `diagnostic_report.render()` `:479` | `step_row['op']` | **No** |
| `dev_test`'s markdown table (`cli_handlers.py`) | `r.op` in an f-string | **No** |
| `submit.py` `:174`, `:606` | `dedup_fingerprint` only | **No** |
| `tools/parse_devtest_issue.py` | groups by the *embedded* fingerprint; accepts `schema_version` by presence only | **No** |
| **all of `tools/*.py`** | grep for op/verdict literals returned **zero hits** | **No** |

Two things inside `chip_test.py` **do** need explicit entries, and both **fail closed by construction** if forgotten (proven by the 121-06 deliberate-break test):
- `_DESTRUCTIVE_OPS` (`:636`) — omission would let a write-shaped op bypass the chip-ID gate.
- `_dispatch_step` (`:924-952`) — an op in neither `{OP_ID, OP_BLANK_CHECK, OP_READ}` nor `_MULTI_RUN_OPS` hits the fail-closed `return StepResult(verdict=VERDICT_BAD, reason="op … matched no dispatch arm")`. So each new op **must** get its own dispatch arm; there is no silent fall-through (that hole was closed in 121-02).

Note these read `Step.op`, not `StepResult.op` — the D-06/D-07 claim is about the latter and remains exactly true.

**Schema consequence:** `SCHEMA_VERSION` bumps `1.2 → 1.3` on the same additive argument the `1.1 → 1.2` bump used (`diagnostic_report.py:55-67`).

**Dedup consequence (a real, statable cost):** because `dedup_fingerprint` hashes `op=verdict:cls` per step, adding four steps **changes the fingerprint for all 43 ALLOW chips**. b14/b15-era reports for the same chip will no longer group with v1.30-era reports, so any accumulated N≥2 promotion count for those chips resets. This is the same mechanism D-08 deliberately relied on to keep partial and full runs apart — here it is a cost rather than a feature, and should be stated, not discovered.

### 1.4 Finding: the leg needs a flags channel the engine does not have today

`_dispatch_multi_run` calls `operator.write_eprom(name, eprom_data, tmp_source_path)` (`chip_test.py:1112`) — **no `operation_flags` argument is passed anywhere in the engine.** Step 3 must set `FLAG_SKIP_SDP_UNLOCK` (`constants.py:121`, `0x100`).

Minimal in-pattern extension: `chip_test.py` already imports a flag constant from `constants` (`FLAG_CAN_ERASE`, `:36`), so importing `FLAG_SKIP_SDP_UNLOCK` and passing `operation_flags=` to the existing `write_eprom` is a one-constant, one-kwarg change. It does brush the module's "sets no VPP, builds no wire dict" contract, so the contract wording should be *narrowed deliberately* rather than silently violated. The alternative — a new operator method — would duplicate `write_eprom` and is worse.

---

## 2. Result-status semantics for the INVERTED assertion

### 2.1 The existing status vocabulary, and why NO new status is needed

`dev test` has five statuses (`chip_test.py:620-624`), and `marginal` **already means exactly "inconclusive"**, wired end-to-end:

| Status | Exit contribution | `build_db_diff` disposition | `ladder_state` | Counts as "ran"? |
|---|---|---|---|---|
| `OK` | 0 | candidate for community-reported | `community-reported` | yes |
| `BAD` | **1** | **community-fail signal** | `community-fail` | yes |
| `marginal` | **2** | **inconclusive — needs N≥2 agreement** | *(none)* | **yes** |
| `NA` | 0 | — | — | no |
| `SKIPPED` | 0 | — | — | no |

Verified at `cli_handlers.py:1862-1868` (exit map), `diagnostic_report.py:290-301` (dispositions), `chip_test.py:1209` (`_RAN_VERDICTS` includes `MARGINAL`).

**A sixth status would open a false-green path.** `_verdict_code` is `_VERDICT_EXIT_CODES.get(verdict, 0)` (`cli_handlers.py:1876`) — **an unrecognised verdict string exits `0`.** It would also miss every arm of `build_db_diff`, landing in the final `else` → `no change suggested` / no ladder tag, silently discarding the finding. Introducing a new status is therefore an **anti-feature** (§5). Use `marginal`.

`marginal`'s documented scope is "destructive/verify-only, never forced onto read-step disagreement" (`chip_test.py:618-619`). An inhibited-write step is destructive-shaped, so `marginal` is in-family, not a stretch.

### 2.2 The complete outcome matrix for `write-inhibited`

Observable inputs: (a) the preceding `sdp-lock` step's verdict; (b) whether firmware acked the opt-out (`MSG_WARN_SDP_UNLOCK_SKIPPED` / `0x86` in `comm.seen_message_ids`); (c) read-back bytes vs pattern A; (d) exceptions.

| # | Condition | Verdict | Rationale |
|---|---|---|---|
| 1 | lock `OK` + opt-out acked + read-back **equals pattern A in every byte** | **`OK`** | The only evidence-bearing green. Claim is bounded: "consistent with the lock inhibiting the write" |
| 2 | lock `OK` + opt-out acked + read-back **fully equals pattern B** | **`BAD`** | Trap 2's target: the lock did not reach silicon. An unexpected success is the failure signal — **never** `SKIPPED`/`NA` |
| 3 | lock `OK` + opt-out acked + read-back **partially changed** | **`BAD`** + `_diff_offsets` count/pct/first-offset in `reason` | gh#11's exact symptom. Never `OK` |
| 3a | …and `classify_fingerprint` returns `blank/contact` or `transport` | **`marginal`** | The read-back *input* is corrupt (≥98 % `0xFF`, or a transport bucket), so the oracle has no valid input. **Non-laundering proof obligation:** branch 2 cannot reach here — pattern B is the complement of an address fold and is never ≥98 % `0xFF`, so a full change to B can never be reclassified as `blank/contact`. This must be a *test*, not an argument |
| 4 | preceding `sdp-lock` verdict is `BAD`/`SKIPPED` (e.g. `MSG_ERR_UNKNOWN_CMD` on pre-Phase-119 firmware) | **`SKIPPED`** — "no lock was emitted; nothing to test" | The **one** legitimate skip. Decided *before* the write, from an independent step's verdict, and **no write is issued**. Structurally not a downgrade of an unexpected success |
| 5 | opt-out **not acked** (no `0x86`) | **`marginal`** | The experiment was not performed as designed — firmware auto-unlocked anyway, so read-back equality *or* inequality is unattributable. Independent evidence, never derived from the write outcome. Prevents a spurious `community-fail` ladder tag on a merely-out-of-date firmware |
| 6 | `EpromOperationError` / timeout / brownout during the write | **`marginal`** | Trap 1: "the write reported failure" is not evidence. **Also not `BAD`** — a comms fault is not a lock finding. Note this **overrides** `_run_step`'s generic `except EpromOperationError → VERDICT_BAD` arm (`chip_test.py:887-894`), so the leg must catch inside its own dispatch arm. Preserve `error_code` |
| 7 | read-back raises, or returns empty/short | **`marginal`** | Oracle input missing. Never `OK` |
| 8 | chip-ID mismatch closed the destructive gate | **`SKIPPED`** for all four leg ops as a group | All four are in `_DESTRUCTIVE_OPS`, so they gate shut together and no lock is emitted. **UNREACHABLE TODAY — see §2.6** |
| 9 | capability-REFUSED chip | **`NA`** carrying the reason, no operator call | `run_plan:780-782`, existing mechanism |
| 10 | chip absent from the DB | *unreachable* | SAFE-04 hard-fails at the top of `dev_test` before any hardware is energized (verified) |

**Every branch has a named status. No branch yields `OK` except branch 1.** The three `marginal` branches (3a, 5, 6/7) are each keyed on **independent** evidence — read-back classification, an ack bit, an exception — never on "the write succeeded", which is what keeps Trap 2 shut.

### 2.3 Companion matrices

`sdp-unlock`: emitted `OK` ⇒ `OK`; raised/not-OK ⇒ `BAD` **plus the recovery line**; lock never emitted or gate closed ⇒ `SKIPPED` ("nothing to undo").

`write-restored`: read-back equals pattern A ⇒ `OK`; differs ⇒ `BAD` **plus the recovery line**; unlock skipped ⇒ `SKIPPED`.

### 2.4 Finding: `write_eprom` already consumes the `0x86` ack — and its return value is ambiguous

`eprom_operations.py:1654-1666` sets `is_ok = False` when `FLAG_SKIP_SDP_UNLOCK` was requested on a `0x0D` write but no `MSG_WARN_SDP_UNLOCK_SKIPPED` was observed. Consequence for the leg: **`write_eprom()` returning `False` on step 3 conflates two entirely different worlds** — "the write was inhibited (expected!)" and "the opt-out was never honoured (inconclusive)". This is precisely why the bool cannot be the oracle, and why branch 5 needs the ack readable as a *separate* signal rather than folded into the return value.

### 2.5 Multi-run policy

Existing destructive/verify steps run twice (`runs=2`, D-05). Recommendation: give each leg op its **own** single-sequence dispatch arm (they are not in `_MULTI_RUN_OPS`), because the leg's four steps are an *ordered sequence* whose meaning depends on order — naively running each twice would emit lock·lock·write·write·unlock·unlock and destroy the sequence semantics. If N≥2 confidence is wanted for the oracle specifically, repeat step 3's write **inside** its own arm and apply the existing disagreement-⇒`marginal` policy there. This is a planning decision, not a research finding; both options are safe.

### 2.6 **Finding: the chip-ID destructive gate is structurally vacuous for the entire SDP-leg population**

Measured live: **all 43 capability-ALLOWED `0x0D` chips have `chip-id == 0`.** Therefore `derive_plan` always emits `Step(op=OP_ID, supported=False, reason="no chip-id in DB entry")` (confirmed for `AT28C256`), and `_id_step_closes_gate`'s documented behaviour is that **an `NA` id step does not close the gate** (`chip_test.py:804-806`). So:

- Matrix branch 8 is **unreachable today**. It must still be specified (it is the correct behaviour if a chip-id is ever added, and `_DESTRUCTIVE_OPS` membership is correct defence-in-depth) but it must be **labelled unreachable**, not presented as live protection.
- The SDP leg's only real pre-flight protections are `sdp_capability()` and `_ALWAYS_WRITES_NOTICE`. There is **no identity check**: a user who sockets the wrong 28-pin part gets it locked.
- **Requirements must not claim "the leg is gated by chip ID."** That would be an overclaim of exactly the v1.22 C-5 class. It makes the §3 recovery line more load-bearing, not less.

---

## 3. The recoverability report line

### 3.1 Wording — "rewrite", never "erase"

Protocol `0x0D` has **no erase operation at all** (`chip_test.py:562-565`, and `write`'s own `--skip-erase` arm says so). Every proposed string below uses *rewrite*; none uses *erase*.

**Loud form** — when the lock was emitted and the run did not confirm the part is unlocked again (`sdp-unlock` or `write-restored` not `OK`):

> `⚠ AT28C256 MAY STILL BE SDP-LOCKED. The lock sequence was emitted but this run did not confirm the part was unlocked again. Protection state cannot be read back on this chip family, so nothing here can tell you which state it is in. To clear it, just rewrite the part: `firestarter write AT28C256 <file>` — the automatic SDP unlock at the start of every protocol-0x0D write clears the protection. There is no erase operation on this family; a rewrite is the recovery.`

**Neutral form** — happy path:

> `AT28C256 was left unlocked: the unlock sequence was emitted and the part accepted a write afterwards. Protection state is not readable on this family, so this is evidence, not a guarantee. Any future `firestarter write` also unlocks automatically.`

### 3.2 Where, and does it print on the happy path?

**Both, with different intensity — and yes, a line prints on the happy path.** Rationale:

- **Per-step** (`StepResult.reason`): required. It is the machine-readable, submitted-with-the-report record, and `dedup_fingerprint` **deliberately excludes `reason`** (`diagnostic_report.py:190-195`), so putting recovery text there cannot perturb dedup grouping.
- **Per-run console summary** (`click.echo`, mirroring `_ALWAYS_WRITES_NOTICE`'s unconditional print at the top of `dev_test`): required. The step reason is buried in a table; an aborted run is precisely the case where a stranger needs one unmissable instruction. `click.echo` not `logger.*` — the same reasoning `dev_sdp`'s D-10 line already records ("so this always reaches the user's console/CliRunner capture regardless of log-level wiring").
- **On the happy path: print the neutral form, not the loud form.** An unconditional *warning* trains dismissal, which would cost exactly the case it exists for. But printing nothing means the note's "the run must end unlocked, **and the report must say so**" is unmet — silence is not a statement. A one-line neutral confirmation of the end state is honest, cheap, and keeps the warning's signal intact.
- **No new `to_dict()` field.** Encode it in step `reason` text only. This keeps the D-06/D-07 discipline (no consumer learns a new field) and keeps `tools/parse_devtest_issue.py` untouched.

**Ctrl-C / cable-yank caveat, stated honestly:** a hard abort between steps 2 and 4 means *no* summary line prints, because the process is gone. The mitigation is not a Python-level guarantee (a `finally`-emitted unlock would itself be an unverifiable serial write into a dying process); it is that the **loud form's text is also in the docs and release notes**, and that `_ALWAYS_WRITES_NOTICE` — printed *before* anything happens — should be extended to name the locked-abort possibility up front, where it is guaranteed to be seen. Do not claim a `finally` handler makes the abort case safe.

---

## 4. `write --sdp-relock` behaviour

### 4.1 Help text

```
--sdp-relock   After a successful write AND a passing verify, emit the SDP
               lock sequence so the part refuses further writes. Protocol-0x0D
               parts only. The resulting protection state CANNOT be read back
               on this family, so this is never a claim about the chip's actual
               state -- only that the sequence was emitted. If the verify does
               not pass, the relock is SKIPPED and reported: the part is left
               unlocked and rewritable rather than locked around a bad image.
```

### 4.2 Observable surface

| Situation | Output | Exit |
|---|---|---|
| **Relock performed** | `AT28C256: write verified; SDP lock sequence was emitted. The resulting protection state cannot be read back on this chip family, so this is not a claim about the chip's actual state. To write this part again just run `firestarter write` — the automatic SDP unlock clears the protection; there is no erase operation on this family.` | 0 |
| **Relock skipped — verify failed** | ERROR level, mandatory + default-visible: `AT28C256: --sdp-relock was requested but the write did NOT verify — the relock was SKIPPED. Locking now would protect an image known to be wrong behind a state that cannot be read back and can only be cleared by another write. The part is left unlocked and rewritable.` | non-zero (the failed verify already drives this) |
| **Relock on a non-0x0D chip** | Warn-and-proceed **without relocking**: `…--sdp-relock has no effect on this chip's protocol (observed protocol N) — SDP is a protocol-0x0D feature. Proceeding with a normal write.` | unchanged |
| **Relock on a capability-REFUSED 0x0D chip** | **Refuse up front, before any hardware is energized**, with `sdp_capability()`'s reason verbatim | 1 |
| **Relock emission itself fails** | `BAD`-equivalent error naming the state as indeterminate, plus §3.1's loud recovery wording | non-zero |

Two deliberate departures from `--skip-sdp-unlock`'s precedents, each with a reason:

- **Non-0x0D: warn but do *not* act.** `--skip-sdp-unlock`'s D-18 arm still emits the flag bit, justified by "a blanket-flag script across a mixed batch must produce identical wire frames." That argument does not transfer: relock is a **separate command (CMD 10)**, not a bit on the write frame. Issuing CMD 10 at a non-`0x0D` part would be actively wrong, and *not* issuing it changes no write frame — so wire-identity is preserved by inaction.
- **Capability-REFUSED: refuse, do not auto-skip.** `write` currently *auto-sets* `--skip-sdp-unlock` for this subset precisely because the lock/unlock sequence's bytes get stored as data at bus-truncated magic addresses on a part with no SDP decoder. Relocking such a part would walk straight into that hazard. Unlike the verify gate, this is knowable before any hardware is energized and the user's intent cannot be honoured *at all* — so refuse, mirroring `dev_sdp`'s Gate-2-outranks-everything ordering (`cli_handlers.py:2235-2243`). **This is where the deleted command's Gate 2 gets repurposed rather than discarded.**

### 4.3 Interaction with `--skip-sdp-unlock`: compatible, not contradictory

They act at **opposite ends of the same write**: `--skip-sdp-unlock` declines the *pre*-write unlock; `--sdp-relock` adds a *post*-write lock.

- `--skip-sdp-unlock --sdp-relock` on an already-locked part = "don't unlock, write (which will fail), then lock" — the write/verify fails, the verify gate skips the relock. Coherent, and safe.
- `--skip-sdp-unlock --sdp-relock` on an unlocked part = "write without the redundant unlock, then lock" — arguably the *cleanest* combination for the AT28C-destined-for-a-live-machine use case.

**Do not make them mutually exclusive** (see anti-features). No extra warning is needed beyond what each flag already prints.

### 4.4 Interaction with `dev test`: none, deliberately

`dev test` takes zero options since Phase 121 D-05 and must never grow `--sdp-relock` or a `--leave-locked`. The leg always ends unlocked; that is the whole point of step 4.

### 4.5 Does it need a confirmation prompt? **No.**

1. `write` has no prompt for any destructive action today; adding one breaks every script that drives it.
2. The flag *is* the consent. `dev_sdp`'s own D-05 records that "a flag mandatory on every invocation carries no information" — the inverse holds: an **optional** flag the user typed is informed consent.
3. The state is recoverable by a plain `firestarter write` (design note §6), so the blast radius is one extra command, not a bricked part.
4. `dev_sdp`'s prompt existed because the lock was that command's *entire* effect. On `write`, the relock rides an operation the user already consented to.

Do carry over the **mandatory, default-visible report line** instead — the precedent `write`'s D-04 auto-set block already sets ("always prints a mandatory, default-visible report line when it fires"). And do **not** add a `-y`/off-TTY refusal: `dev_sdp`'s Gate 4 inverted `dev test`'s off-TTY behaviour specifically because it had no consent flag; `--sdp-relock` *is* one.

### 4.6 How comparable programmers surface a deliberate write-protect

**minipro** (upstream `gitlab.com/DavidGriffith/minipro`, `man/minipro.1`, fetched verbatim):

```
-u, --unprotect     Disable protection before programming.
-P, --protect       Enable protection after programming.
```

Three points, all favourable to the v1.30 design:

1. **No standalone `protect`/`unprotect` subcommand exists** — the reference implementation for this entire class of hardware exposes protection control *only* as flags on the write operation. That is independent support for retiring `dev sdp` and re-homing the lock on `write`.
2. **No read-back/status query exists either** — nobody in this space offers one, consistent with the AT28C datasheets documenting a 3-byte enable/disable command sequence and **no status bit**.
3. **minipro's `-P` is not verify-gated** — it protects after programming unconditionally. Firestarter's verify-gated skip is therefore *stricter than the reference implementation*, which is a defensible differentiator rather than an oddity.

Firestarter differs in one direction worth noting: its unlock is **default-on** (firmware auto-unlocks every `0x0D` write) where minipro's is opt-in `-u`. That asymmetry is exactly what makes the `dev sdp` deletion safe (§6 of the design note) and is the dependency to re-examine if that default is ever revisited.

*Confidence: LOW per the provider tier (web-sourced), though the man page was fetched from the upstream repository directly. Some third-party/older docs describe inverted-polarity variants (`-u` = "Do NOT disable write-protect"); no changelog entry corroborates a historical inversion, so that variant is noted and not relied on.*

---

## 5. What the deleted command's users see

### 5.1 Click's native behaviour — measured, not assumed

Run against the live tree with Click 8.3.3:

```
$ firestarter dev nosuchcmd
Usage: firestarter dev [OPTIONS] COMMAND [ARGS]...
Try 'firestarter dev --help' for help.

Error: No such command 'nosuchcmd'.
$ echo $?
2
```

So the error **is** usable: it names the offending token, prints usage, and points at `--help` (which lists surviving commands), exiting 2. It offers no "did you mean" and says nothing about a replacement.

### 5.2 Recommendation: **clean removal from the CLI, with the substitution documented outward**

Arguments for:

- **In-repo precedent, one milestone old.** Phase 121 removed four `dev test` flags with *no* transitional message — only Click's native error — and locked that in with tests asserting each removed flag errors (`tests/test_dev_test_cmd.py:180-227`). Treating a removed *subcommand* differently from removed *options* needs a reason, and there isn't one.
- **A transitional stub keeps the command registered in the `dev` group** — which is precisely the artifact 999.15's channel split then has to classify. That reintroduces the host/firmware namespace collision the retirement was chosen to *dissolve* (design note §2, final bullet).
- **The right channel for "what replaced it" already exists and is already owed.** The gh#12 follow-up and the release notes are dated, versioned, and reach the exact population that saw the b14 instruction. A CLI string reaches only the subset who both installed a `--pre` build *and* retype the old command.
- **Blast radius is days of pre-release installs**, and no stable release ever carried the command.

Considered and rejected: a `hidden=True` stub that prints the substitution and exits non-zero. It targets the stranded instruction precisely, but it (a) stays in the `dev` group for 999.15 to classify, (b) becomes a permanent maintenance item with no scheduled removal, and (c) is invisible in `--help` anyway, so it only ever helps a retyper. Cheap to reverse if the operator disagrees — this is a judgement call, not a technical constraint.

**What the removal must carry instead:** a test asserting `dev sdp` errors (the direct analogue of `test_dev_test_rejects_each_removed_flag`), so the removal is pinned rather than merely done.

### 5.3 **Finding: deleting the test file breaks a fail-closed gate**

`tools/check_no_exists_proxy.py` carries an explicit target list that names **`tests/test_dev_sdp_cmd.py`** (`:156`), and `:328-332` **exits 1 when any listed target is missing** ("…vacuously pass with a target silently skipped"). So `git rm tests/test_dev_sdp_cmd.py` **turns that gate RED unless the list is updated in the same commit.** This is the same class as the known "milestone close breaks its own record gates" trap and should be a named requirement, not a discovery during execution.

Of the file's 14 tests, several are worth **repurposing rather than deleting** — notably `test_no_fabricated_lock_state_boolean_in_the_report` (`:453`) and `test_summary_line_carries_the_unreadable_state_caveat_on_both_directions` (`:395`), whose invariants apply verbatim to the new leg and to `--sdp-relock`.

---

## 6. Feature Landscape

### Table Stakes (users expect these / the product is broken without them)

| Feature | Why Expected | Complexity | Notes / dependencies |
|---|---|---|---|
| **Delete `dev sdp`** | A command whose success line admits it proves nothing is surface debt; 999.15 removes it from stable anyway | **LOW–MEDIUM** | Clean tail truncation (`cli_handlers.py:2193-2318`). **Depends on** auto-unlock staying default-on (§6 of the note — record the dependency), `sdp_capability.py` surviving in full, `COMMAND_NAMES` entries surviving (`KeyError` at `eprom_operations.py:329`/`:405` otherwise), **and** updating `check_no_exists_proxy.py:156` |
| **`write --sdp-relock`** | The only legitimate need `dev sdp` served (an AT28C destined for a live machine); gh#12 asked for it; minipro's `-P` is the class norm | **MEDIUM** | Depends on `sdp_lock` (`:1784`), `sdp_capability`, the verify outcome, and slotting beside `write`'s existing D-04 auto-set block |
| **Recoverability report line** | An aborted run ships a locked chip to a stranger; §2.6 shows there is no identity gate behind it | **LOW** | Wording only; must say **rewrite**, never erase. No new report field |
| **mypy gate-hardening → primary `ci` GREEN** | A **fail-open** gate is worse than no gate: it reported green while type-checking nothing, hiding 69 errors against a watermark of 35 | **MEDIUM–HIGH** | `check_mypy_watermark.py:56` shells to a bare `mypy` from `PATH`; devcontainer py3.12 vs configured `python_version = "3.9"`. Independent of every SDP item — can run in parallel |
| **gh#12 outward follow-up** | A published instruction (2026-07-30) is stranded one day later; integrity | **LOW** | Wording + operator review. Must state the substitution honestly and must not let "now provable" drift into "now proven" |

### Differentiators (genuine competitive advantage)

| Feature | Value Proposition | Complexity | Notes / dependencies |
|---|---|---|---|
| **Plan-derived SDP leg in `dev test`** | The **only oracle in existence** for this feature — protection is unreadable on `0x0D`, so lock→inhibited-write→read-back is the sole evidence path. No comparable programmer offers *any* verification of protection state | **HIGH** | Depends on: `sdp_capability` (signature already `(name, db)` — **zero plumbing**, verified), `derive_plan`, `_DESTRUCTIVE_OPS`, four new `_dispatch_step` arms, `FLAG_SKIP_SDP_UNLOCK` + the `0x86` ack, `generate_pattern`/`_diff_offsets`/`classify_fingerprint`, `SCHEMA_VERSION` 1.2→1.3 |
| **Verify-gated relock** | Stricter than minipro's unconditional `-P`; never locks a known-bad image behind an unreadable state clearable only by another write | **LOW** (given the flag) | Rides `write`'s existing verify result |
| **Evidence returns to the repo** | The leg files through `submit_report`, so a stranger's silicon result reaches the maintainer instead of dying in their terminal | **LOW** (already built) | Unchanged `submit.py`; note the dedup-fingerprint reset in §1.3 |
| **999.15 / gh#8 dev-tools channel gating** | Stable users get a surface that cannot hurt them; beta keeps the sharp tools. The channel is the gate — never an env var (fails open) | **MEDIUM** | `channel.py::is_prerelease_build()`. **Sequencing:** whichever of this and the `dev sdp` deletion lands first shrinks the other's diff; the deletion removes one subcommand this would otherwise classify |

### Anti-Features (explicitly do NOT build)

| Anti-Feature | Why Requested | Why Problematic | Instead |
|---|---|---|---|
| **Any option on `dev test`** (`--sdp`, `--no-sdp`, `--skip-sdp-leg`, `--leave-locked`) | "Let users opt out of the destructive leg" | Violates Phase 121 D-05's zero-option surface; the four v1.21 flags were **removed, not disabled** | **Plan-derive** the leg from `sdp_capability()` in `derive_plan`, like every other step |
| **A new verdict/status for "inconclusive"** | "BAD is too harsh for a transport fault" | **False green:** `_verdict_code` is `.get(verdict, 0)` → unknown verdicts exit **0**; and it misses every `build_db_diff` arm, discarding the finding | Reuse **`marginal`** — already exit 2 + "inconclusive — needs N≥2 agreement" + no ladder tag |
| **Downgrading an unexpected write success to `SKIPPED`/`NA`** | "The lock clearly isn't supported, so the step is inapplicable" | Trap 2 — inverts the leg's entire sensitivity. An unexpected success **is** the failure signal | **`BAD`** (matrix branch 2), unconditionally |
| **Using `write_eprom()`'s bool as the oracle** | It's right there and it's cheap | Trap 1 — every unrelated failure returns the same `False`; §2.4 shows the bool *already* conflates two worlds via the `0x86` ack check | **Read-back equality against pattern A**, byte for byte |
| **Reporting a partial change as `OK` or `marginal`-by-default** | "Mostly unchanged is basically unchanged" | gh#11's exact symptom | **`BAD`** with diff count + first offset; `marginal` **only** via 3a's independently-evidenced corrupt-read-back path, with a test proving branch 2 can't reach it |
| **A "is it locked?" query, or a `lock_state: bool` in the report** | The obvious thing to want | Physically impossible on `0x0D` (Phase 117 D-05 / Phase 119 D-12; datasheets document no status bit). `test_no_fabricated_lock_state_boolean_in_the_report` already forbids it | **Repurpose** that test onto the new leg and `--sdp-relock` |
| **Making `--sdp-relock` and `--skip-sdp-unlock` mutually exclusive** | "They sound contradictory" | They act at opposite ends of one write and their combination is *coherent* — and on an unlocked part it is the cleanest form of the intended use case | Allow both; each keeps its own existing message |
| **A confirmation prompt (or `-y`) on `write --sdp-relock`** | `dev sdp` had one | `write` has no prompts and scripts depend on that; the optional flag **is** consent; the state is recoverable in one command | Mandatory default-visible report line, per `write`'s D-04 precedent |
| **Wording recovery as "erase"** | Habit from other families | `0x0D` has **no erase operation at all** — the instruction would be unfollowable | **"rewrite"** everywhere (§3.1 strings comply) |
| **A permanent transitional `dev sdp` stub** | The stranded gh#12 instruction | Stays registered in the `dev` group for 999.15 to classify, has no removal date, and is `--help`-invisible anyway | Clean removal + a test pinning it + the substitution in the release notes and gh#12 reply |
| **Relocking regardless of verify** (or refusing the whole write up front) | "The user asked for a lock" | Protects a known-bad image behind an unreadable state clearable only by another write; contradicts auto-unlock policy (d) — "the attractor should be the state the user can recover from" | Skip the relock, **report it loudly**, leave the part rewritable |
| **Raising the mypy watermark to 69 to turn `ci` green** | Fastest path to a green badge | Ratifies the debt the fail-open gate was hiding and re-arms the same trap | Fix the invocation (pinned interpreter / `python -m mypy`, `python_version` reachable) **then** drive the count down; the watermark only ever moves down |
| **Re-adding the capability as `dev sdp-lock` / `dev sdp-unlock`** | "Just rename it" | Same unverifiable surface, same 999.15 collision, now with two names | The leg (evidence) + `write --sdp-relock` (production) |

---

## 7. Feature Dependencies

```
mypy gate-hardening (item 4)
    └── independent of everything else — parallelizable from day 1

Delete dev sdp (item 1)
    ├──requires──> auto-unlock stays default-on          [design note §6 — RECORD, revisit together]
    ├──requires──> sdp_capability.py survives in full     [serves 3 consumers now]
    ├──requires──> COMMAND_NAMES entries survive          [KeyError at eprom_operations.py:329/:405]
    ├──requires──> check_no_exists_proxy.py:156 updated   [fail-closed at :328-332]
    └──enables───> 999.15 channel gating (item 5)         [one fewer subcommand to classify]

dev test SDP leg (item 2)
    ├──requires──> sdp_capability(name, db)               [signature already matches derive_plan — zero plumbing]
    ├──requires──> new ops in _DESTRUCTIVE_OPS + 4 dispatch arms   [both fail closed if forgotten]
    ├──requires──> FLAG_SKIP_SDP_UNLOCK reachable from the engine  [NEW: no flags channel today, §1.4]
    ├──requires──> the 0x86 ack readable as a SEPARATE signal      [§2.4 — else branches 2 and 5 merge]
    ├──requires──> sdp_lock / sdp_unlock                 [eprom_operations.py:1784 / :1736]
    ├──reuses────> generate_pattern, _diff_offsets, classify_fingerprint
    ├──forces────> SCHEMA_VERSION 1.2 -> 1.3             [additive; parse_devtest_issue unaffected]
    └──costs─────> dedup_fingerprint change for all 43 ALLOW chips [N>=2 counts reset]

write --sdp-relock (item 3)
    ├──requires──> sdp_lock                              [shared with item 2]
    ├──requires──> sdp_capability                        [shared; capability refusal = up-front refuse]
    ├──requires──> write's verify outcome                [the gate]
    └──repurposes> dev sdp's Gate 2 ordering             [capability outranks support-status]

Recoverability line
    └──requires──> the leg's step verdicts (item 2) AND the relock's outcome (item 3)

gh#12 follow-up (item 6)
    └──requires──> items 1 and 3 landed  [it describes the substitution; writing it earlier would describe a plan, not a fact]

items 1 and 3 ──must land together──> deleting the lock before re-homing it strands the only legitimate use case
item 2 ──conflicts with──> any dev test option  [Phase 121 D-05]
```

### Dependency notes

- **`sdp_capability`'s signature is already `(chip_name, db)`** — identical to `derive_plan(name, db, …)`. Verified. The applicability predicate drops into plan derivation with no threading, no new parameter, no context object.
- **The engine has no `operation_flags` channel** (§1.4). This is the one genuinely new seam item 2 needs.
- **Items 1 and 3 are a pair.** Landing the deletion without the relock removes the only legitimate capability the command served, in a released pre-release. Landing the relock first is safe in isolation.
- **Item 4 is fully independent** and gates nothing — but it gates *everything* in the sense that a RED primary `ci` job means no other item's evidence is trustworthy. Front-load it.

---

## 8. Prioritization

| Feature | User Value | Implementation Cost | Priority |
|---|---|---|---|
| mypy gate-hardening (primary `ci` GREEN) | MEDIUM (invisible to users, load-bearing for every other claim) | MEDIUM–HIGH | **P1** — front-load; a fail-open gate makes all other evidence suspect |
| `write --sdp-relock` | HIGH (the only real user need; gh#12's ask) | MEDIUM | **P1** |
| Delete `dev sdp` | MEDIUM (surface honesty, 999.15 unblock) | LOW–MEDIUM | **P1** — must ship with the relock |
| `dev test` SDP leg | HIGH (the only oracle in existence) | HIGH | **P1** — the milestone's reason to exist |
| Recoverability line | HIGH (protects a stranger's part) | LOW | **P1** — ships with the leg |
| 999.15 / gh#8 channel gating | MEDIUM–HIGH | MEDIUM | **P2** — sequence after the deletion to shrink its diff |
| gh#12 follow-up | MEDIUM (integrity) | LOW | **P2** — after 1 and 3 land; operator wording review |

All six are P1/P2: this is a debt-and-proof milestone with no speculative scope. There is no P3.

---

## 9. Evidence ceiling (must be stated in requirements, not discovered at close)

No AT28C part has ever been in operator inventory; `0x0D` remains `UNVERIFIED`.

- **Provable this milestone:** the *emission* (correct sequence, pinout remap, `/WE` asserted) via the Phase 116 trace harness; the *plan derivation* (43 ALLOW get four steps, 41 REFUSE get four NA steps carrying reasons — measurable today with zero hardware); the *read-back comparison logic* and **every branch of the §2.2 matrix** in the native envs with a stubbed operator.
- **NOT provable this milestone:** the causal claim *"the lock inhibited the write."* Reachable only on silicon, i.e. only from a community `dev test` report, which by design does not gate the close.
- **Additionally not provable, and newly discovered:** §2.6 — there is no identity gate behind the leg for any chip that reaches it, so "the leg is chip-ID gated" must not appear in any requirement.

Writing requirements that conflate the first bullet with the second reproduces v1.22's C-5 overclaim.

---

## 10. Competitor Feature Analysis

| Feature | minipro (upstream) | Firestarter today (b15) | v1.30 plan |
|---|---|---|---|
| Disable protection before write | Opt-in `-u/--unprotect` | **Default-on** in firmware, opt-out `--skip-sdp-unlock` | Unchanged (and it is *why* the deletion is safe) |
| Enable protection after write | Opt-in `-P/--protect`, **not** verify-gated | `dev sdp <chip> enable` (standalone, unverifiable) | Opt-in `write --sdp-relock`, **verify-gated** — stricter than the reference |
| Standalone protect/unprotect command | **None** | `dev sdp` | **Deleted** — converges on the class norm |
| Read back protection state | **None** | None (impossible on `0x0D`) | None, and explicitly forbidden as an anti-feature |
| Verify that protection actually works | **None** | None | **The `dev test` SDP leg** — no comparable tool does this |

---

## Sources

- **Live tree** `firestarter_app` @ `beta` `16a313a` — `chip_test.py`, `diagnostic_report.py`, `cli_handlers.py`, `eprom_operations.py`, `constants.py`, `sdp_capability.py`, `tools/check_no_exists_proxy.py`, `tools/check_mypy_watermark.py`, `tests/test_dev_sdp_cmd.py`, `tests/test_dev_test_cmd.py` — **HIGH** (read directly; all line refs re-verified, stale ones corrected in §0)
- **Live measurement** — 84 `0x0D` chips / 43 ALLOW / 41 REFUSE; all 43 with `chip-id == 0`; `derive_plan("AT28C256", write_scope="full")` step list and `(0, 256)` region; Click 8.3.3 unknown-subcommand error and exit 2 — **HIGH** (executed against the live tree)
- `.planning/notes/sdp-surface-retirement-and-behavioral-proof.md` §§1–9 — authoritative design note
- `.planning/PROJECT.md` §"Current Milestone: v1.30" (lines 38–155); `.planning/research/questions.md` §999.25 (lines 195–221)
- [minipro man page, `man/minipro.1`, gitlab.com/DavidGriffith/minipro](https://gitlab.com/DavidGriffith/minipro) — `-u/--unprotect`, `-P/--protect` quoted verbatim — **LOW** per provider tier (upstream repo, fetched directly)
- [minipro man page rendering, ManKier](https://www.mankier.com/1/minipro) — corroborating — **LOW**
- [AT28C256 datasheet, Microchip](https://ww1.microchip.com/downloads/en/DeviceDoc/doc0006.pdf) and [AT28C64B datasheet](https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/AT28C64B-64-Kbit-8Kx8-Parallel-EEPROM-with-Page-Write-and-Software-Data-Protection-DS20006432.pdf) — 3-byte SDP enable/disable sequences, ships SDP-disabled, survives power cycling, **no status bit documented** — **LOW** per provider tier, but primary-source corroboration of Phase 117 D-05 / Phase 119 D-12
- [Microchip Device Operation docs](https://onlinedocs.microchip.com/pr/GUID-BF812ABD-A95E-4E56-B54E-14AA4CC3999A-en-US-1/GUID-D6DBCF7C-05FF-418D-8F92-F6EC72BB55D4.html) — SDP behaviour on a protected part — **LOW**

---
*Feature research for: v1.30 SDP Surface Retirement & Behavioral Lock Proof*
*Researched: 2026-08-03*
