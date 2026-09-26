# Feature Research — v1.22 AT28C Software Data Protection Lifecycle

**Domain:** Write-protection (SDP) lifecycle as a user-facing feature on a parallel-EEPROM programmer (protocol `0x0D` / `configure_eeprom28c`)
**Researched:** 2026-07-27
**Confidence:** HIGH on ground truth + datasheet semantics · MEDIUM on the behavioural prediction in §0.2 (no AT28C silicon on the bench) · MEDIUM on ecosystem naming (two sources, cross-checked, polarity genuinely split)

---

## 0. Ground truth read from the tree (do not trust the backlog narrative)

Every claim in this section was read out of the working tree at v1.22 start, not inferred. **Confidence: HIGH.**

### 0.1 What already exists

| Fact | Evidence |
|---|---|
| SDP-**disable** runs unconditionally + silently on every `0x0D` write | `firestarter/src/proms/eeprom_28c.cpp:104` — `flash_execute_command(EEPROM_SDP_DISABLE)` inside `eeprom28c_write_init()`, no flag, no log, no user-visible signal |
| The 6-write disable table is local to the handler | `eeprom_28c.cpp:26-33` (`EEPROM_SDP_DISABLE`) — a duplicate of `FLASH_DISABLE_WRITE_PROTECTION`, `flash_utils.h:53-60` |
| 64-byte page write + read-back polling exist | `eeprom_28c.cpp:19` (`PAGE_SIZE 64`), `:119-133` (`eeprom28c_write_execute`), `:135-155` (`eeprom28c_wait_for_write`) |
| SDP-**enable** does not exist at any layer | `FLASH_ENABLE_WRITE_PROTECTION` (`flash_utils.h:48-52`) has **zero callers** — confirmed by grep across `src/` |
| That table is byte-identical to `FLASH_ENABLE_WRITE` | Both are `{0x5555,0xAA},{0x2AAA,0x55},{0x5555,0xA0}` (`flash_utils.h:42-46` vs `:48-52`). **Not a copy-paste bug** — see §0.3 |
| No host CLI surface for lock/unlock | `firestarter/cli_handlers.py` — grep for `sdp|protect|unlock` returns only doc-prose hits in `ic_layout.py:270`/`:475` |
| Blast radius | **84 chips** carry `algorithm: 13` (75 `supported`, 9 `adapter-required`) across ATMEL, MICROCHIP memory, XICOR, NEC, CATALYST, EXEL, MAXWELL |

### 0.2 The success proxy is not weak — the datasheet says it is inverted

`eeprom28c_write_init()` proves the SDP-disable landed by polling address `0x5555` for the value `0x20`:

```c
flash_execute_command(EEPROM_SDP_DISABLE);
if (!eeprom28c_wait_for_write(handle, 0x5555, 0x20)) { return; }   // eeprom_28c.cpp:106
```

The AT28C256 datasheet (Microchip DS20006386B, local copy `firestarter_app/datasheets/AT28C256.pdf`, p. 10) states:

> "The data in the enable and disable command sequences **is not written to the device** and the memory addresses used in the sequence may be written with data in either a byte or page write operation."

So on a **successful** disable, `0x5555` retains its original array content — it will **not** read `0x20`. The poll therefore succeeds only when the sequence was *not* recognised as a command (degenerated into ordinary byte writes, e.g. inter-byte time exceeding `tBLC` = 150 µs) or when the array coincidentally already holds `0x20` at `0x5555`. On a blank chip it should time out → `MSG_ERR_EEPROM_TIMEOUT` → `RESPONSE_CODE_ERROR` → `write_init` returns → **the write aborts before a single data byte is sent.**

**Prediction (MEDIUM confidence — datasheet-grounded HIGH, behaviourally unverified because no AT28C part is on the bench): `firestarter write at28c256 <file>` on `3.0.0b11` fails at INIT with an EEPROM timeout, not silently-partially.**

Two independent community data points are consistent with this (§6): pdr0663 on gh#12 reports the write "seems to write nothing before crashing," and the maintainer's own reply is "I haven't had the time to get the 28cXXX to work yet."

**Why this dominates the whole milestone:** the *only* argument for keeping today's silent auto-unlock is backward compatibility (§2). If the current path aborts every write, **that backward-compatibility cost is zero** and the policy design space opens all the way up. This is a cheap native-test question and must be settled in the first phase, **before** the policy REQ is written.

### 0.3 The `AA-55-A0` prefix is dual-purpose — this is the milestone's key mechanic

Datasheet p. 10 + p. 16, cross-read:

- **SDP enable** = write `AA@0x5555`, `55@0x2AAA`, `A0@0x5555`, then 0–64 data bytes. "Write-Protect state will be activated at end of write **even if no other data is loaded**" (p. 16, note 2).
- **Writing while already protected** = "once protected, the host may still perform a byte or page write to the AT28C256. This is done by **preceding the data to be written by the same 3-byte command sequence used to enable SDP**" (p. 10).

The same three writes mean *both things*. Consequences, all load-bearing:

| Chip state before | Write path used | State after |
|---|---|---|
| SDP **on** | prefixed write (`AA-55-A0` + data) | data written, **SDP stays on** |
| SDP **off** | prefixed write | data written, **SDP becomes on** |
| SDP **on** | unprefixed write | **nothing written**, SDP stays on (the gh#12 symptom) |
| SDP **off** | unprefixed write | data written, SDP stays off |

Therefore **`FLASH_ENABLE_WRITE_PROTECTION` is not dead-by-mistake and is not deletable-as-dead-code** — it is the write-through prefix. (Note the abandoned commit `0052c42` from v1.16 Phase 89-01 tried to delete it; per `PROJECT.md` it never merged. Do not resurrect that deletion.)

And critically: **there is no state-neutral universal write path.** Prefixed-always drives every chip toward *protected*; unlock-then-unprefixed drives every chip toward *unprotected*. Both are single code paths needing zero state reads. §2 turns on which terminal state you choose as the attractor.

### 0.4 Two more facts that reshape scope

**The A9-12V identity check is dead in practice.** `eeprom28c_check_chip_id` is guarded by `if (handle->chip_id > 0)` (`eeprom_28c.cpp:95`). **All 84** `algorithm: 13` DB entries carry `chip_id_check: false` and `chip_id_value: "0x00000000"` — verified by iterating `chip_database.json`. The check has never executed for any real chip. Worse, the datasheet (p. 11) says the ID area is "an extra 64 bytes of EEPROM memory … available **to the user** for device identification," writable via A9=12V — it is **not a factory signature**, and reads `0xFF` on a virgin part. See §5 and the anti-feature in §7.

**`firestarter erase at28c256` cannot work, but `dev test` plans it anyway.** `configure_eeprom28c` has only `case CMD_WRITE` and `case CMD_BLANK_CHECK` (`eeprom_28c.cpp:39-47`) — no `CMD_ERASE` arm, so `handle->firestarter_operation_main` stays NULL and `op_execute_function` returns false (`operation_utils.cpp:103-108`). Meanwhile `database.py:594` sets `FLAG_CAN_ERASE` for `electrical.type == "EEPROM"`, and `chip_test.derive_plan` plans `OP_ERASE` whenever `can_erase and protocol != 0x05` (`chip_test.py:404`). So `dev test at28c256 --destructive` will produce a **BAD** erase verdict → `build_db_diff` auto-tags `ladder_state = "community-fail"` (`diagnostic_report.py:268`) **even if write and verify both pass**. That directly poisons the gh#11/gh#12 closeout, which asks reporters to file `dev test` reports. (The datasheet does document an "optional chip erase mode … using a 6-byte software code," p. 11 — so erase is implementable, just not in this scope.)

---

## 1. Feature Landscape

### Table Stakes (users expect these)

| Feature | Why Expected | Complexity | Notes / dependencies |
|---|---|---|---|
| **F1 — SDP-enable (lock) wired in firmware** | The half that does not exist. gh#12's title is literally "Write Protection Enable/**Disable** missing." A programmer that can only remove protection is asymmetric and untrustworthy | **LOW–MED** | Table exists (`flash_utils.h:48`, = the write prefix per §0.3). Needs a command arm + a `tWC` wait (10 ms max, p. 13). **Does not touch array data** (p. 16 note 2) → non-data-destructive. Measure Uno flash: Leonardo sat at 87.7% / 25136 B post-v1.16 |
| **F2 — SDP-disable (unlock) as a standalone operation** | This is *exactly and only* what gh#12's reporter asked for: he built a second Arduino to run the disable algorithm once, then used firestarter normally. One command retires that workaround | **LOW–MED** | Reuses the shipped `EEPROM_SDP_DISABLE` table verbatim. Depends on F1's command plumbing (same CMD arm, opposite direction) |
| **F3 — Today's in-write auto-unlock becomes *observable*** | Silent state mutation of the user's chip is the substance of the "must not fire silently" posture. Reporting it costs nothing and satisfies the objection without breaking anyone | **LOW** | One log/report line in `write` output. This is the cheapest, highest-value item in the milestone |
| **F4 — Honest success/failure reporting for both sequences** | Today's proof is inverted (§0.2). A programmer that reports success it cannot substantiate is worse than one that says "cannot confirm" | **MED** | Design work, not code volume. See §4. Native-testable; must replace the `0x5555 == 0x20` poll |
| **F5 — Truthful "SDP state is not readable on this family" reporting** | Users will ask "is it locked now?" SDP has no status bit on AT28C. `doc/lockable-proms.md` §17: "Usually no explicit SDP flag." An honest refusal is table stakes; a fabricated ✓ is a defect | **LOW** | Reuse the v1.21 `NOT_MEASURED` pattern verbatim (`diagnostic_report.py:59`, D-03/D-04: "honest fallback, never a false 0") |
| **F6 — 3-tier software validation harness** | No AT28C part in operator inventory (confirmed at kickoff). Register-level golden traces are the only available oracle. In-tree precedent: v1.13 harness, v1.16 golden traces | **MED** | Must include a **RED test for the §0.2 inversion** — that is the phase-1 deliverable that unblocks the §2 decision |
| **F7 — gh#11 / gh#12 closeout comments** | Both reporters are still waiting; gh#12 has been open since 2024-09-15 with the maintainer's own question unanswered | **LOW** | Explicitly best-effort — `PROJECT.md` states no requirement depends on a community reply |

### Differentiators (competitive advantage)

| Feature | Value Proposition | Complexity | Notes |
|---|---|---|---|
| **F8 — `--skip-sdp-unlock` opt-out on `write`** | Lets a user who *wants* their chip to stay protected write through it. Neither minipro nor flashrom lets you opt out of the auto-unlock in a documented way — flashrom "automatically tries to disable WP before any operation" with no opt-out flag | **LOW** | Naming per §3. Needs a flag bit — see the allocation note below |
| **F9 — `--sdp-relock` post-write re-lock** | minipro's `-P/--protect` ("enable protection after programming"). Real use case: burning a ROM that ships inside hardware where an inadvertent write is a field failure | **LOW–MED** | Falls out of §0.3 almost free: it *is* the prefixed-write path. Must be gated `if verify passed` — else a failed verify leaves a locked chip the user cannot retry on (the Phase 112 `if destructive:` lesson) |
| **F10 — `dev test` SDP step** | Turns the community sweep into an SDP diagnostic: gh#11's re-test would then *say* whether SDP was involved instead of leaving the maintainer to guess | **MED** | ⚠️ Adding a step to `derive_plan` changes `dedup_fingerprint` for **all** 0x0D chips (`diagnostic_report.py` — the hash walks `report.results` per-step). Breaks cross-report N≥2 agreement against pre-v1.22 reports. Harmless today (zero AT28C reports exist) but must be a stated decision |
| **F11 — Write-probe SDP-state *inference*** | The only behavioural signal available: write a known byte to a scratch address **without** the prefix; landed ⇒ SDP off, unchanged ⇒ SDP on | **MED–HIGH** | `doc/lockable-proms.md` explicitly excludes this from "readable": "It does **not** include merely attempting a write and seeing whether it fails." Must be labelled `inferred`, never `read`. Consumes a write cycle and mutates one byte when SDP is off → `--destructive` only |
| **F12 — Close the `dev test` phantom-erase gap for 0x0D** | Without it, every gh#11/#12 re-test report is auto-tagged `community-fail` on a step the firmware was never able to serve (§0.4) | **LOW–MED** | Two candidate fixes: add a `CMD_ERASE` arm (datasheet 6-byte chip-erase code exists) or make `derive_plan`/`convert_to_programmer` honest for 0x0D. The second is cheaper and in-scope; the first is a feature |

### Anti-Features (see §7 for the full list with rationale)

| Feature | Why Requested | Why Problematic | Alternative |
|---|---|---|---|
| **A1 — `firestarter lock-status <chip>` + curated protection table** | "Just tell me if it's locked" | Explicitly out of scope for v1.22; needs a hand-curated cross-family table (`.planning/seeds/lock-status-command-hand-curated-protection-table.md`). Cross-family scope, own milestone | F5 (honest "not readable") now; the seed later. **Genuine dependency flagged in §7** |
| **A2 — Auto-relock by default** | "Leave the chip safe" | Changes how the chip behaves in the user's downstream hardware without being asked, **and cannot be confirmed** (no status bit). Manufactures new gh#12s | F9 as an explicit opt-in flag |
| **A3 — "Leave it as you found it" as the default** | Most intuitive-sounding policy | **Physically unimplementable**: restoring a state requires reading it, and AT28C SDP state is not readable. Any implementation is a guess wearing a promise | Pick one deterministic attractor (§2) and say which |
| **A4 — Populating `chip_id_value` for AT28C so identity-check works** | "The ID check is dead, let's fix it" | The 64 ID bytes are **user-writable and blank (`0xFF`) on virgin parts** (datasheet p. 11). A populated DB id would make every factory-fresh AT28C fail identity | Leave `chip_id: 0`; treat identity as genuinely unavailable on this family (§5) |
| **A5 — Fail-loud-by-default on a locked chip (option (c))** | Matches "unlock is destructive, never silent" | Breaks the write path for 84 DB chips over a rare condition, contradicts **both** comparable tools, and contradicts the maintainer's own constraint | Option (d) — §2 |
| **A6 — A generic `locked: true/false` DB field** | Simplest schema | `doc/lockable-proms.md` closes with the explicit rule: "A programmer database should **not** use one generic field called `locked`" | The seed's `protection_kind` / `status_readable` / `unlockability` triple — deferred with A1 |

**Flag-bit allocation note (affects F8/F9 complexity):** the flags byte is **fully allocated** — `0x01 FLAG_FORCE` … `0x80 FLAG_VERBOSE`, identically in `firestarter_app/firestarter/constants.py:90-99` and `firestarter/include/firestarter.h:59-68`. `handle->ctrl_flags` is `uint32_t` (`firestarter.h:96`) so `0x100` is available firmware-side, but the host emit path and every 8-bit assumption must be audited. Command codes **9 and 10 are free** (gap between `CMD_DEV_REGISTER 8` and `CMD_READ_VPP 11`), as is 16+. A new CMD code is the cheaper axis. Either way this is **dual-repo lockstep**, and any new message ID goes through `messages.toml` → `codegen.py` (`include/messages.h` is generated — never hand-edit).

---

## 2. The auto-unlock policy question

### The design space, re-framed

§0.3 collapses the abstract five-way choice into one real question. Because SDP state is unreadable, no policy can branch on it. Every implementable policy is a **single unconditional code path**, and each one drives the chip toward one terminal state:

| Option | Mechanism | Terminal state (attractor) | What breaks / who is surprised |
|---|---|---|---|
| **(a) keep silent auto-unlock** | unlock, then unprefixed write | **unprotected** | Nobody's *writes* break. Surprised: the user who deliberately locked their chip and finds it unlocked, with no line of output ever having said so. Fails the project's stated posture on substance (silent mutation), not on outcome |
| **(b) auto-unlock + report it** | (a) + one output line | **unprotected** | Nothing breaks. Nobody is surprised. Does not satisfy a reading of the posture that demands *opt-in*, only the reading that demands *visibility* |
| **(c) unlock only with an explicit flag, else fail loudly** | refuse to write unless flagged | **unprotected**, but only on request | **84 DB chips' `write` starts failing** until every user learns a new flag. Surprised: literally every existing AT28C user, on an upgrade, on a chip that used to work. Contradicts minipro *and* flashrom. Contradicts the maintainer's own "don't overshadow more common functionality" |
| **(d) auto-unlock by default, reported, with an opt-out** | (b) + `--skip-sdp-unlock` | **unprotected** by default, **as-found** when flagged | Nothing breaks. The deliberate-locker gets a documented escape hatch. Cost: one flag bit + one doc paragraph |
| **(e) auto-unlock then auto-re-lock** | prefixed write (§0.3 makes this one path, not two) | **protected** | Surprised: everyone downstream. The chip now silently rejects unprefixed writes from *any* other tool and from older firestarter builds — i.e. this **manufactures the gh#12 bug for the next user**. And the re-lock **cannot be confirmed** |
| **(f) write-through-SDP** *(not in the original design space — surfaced by the datasheet)* | prefixed write, always | **protected** (same as (e)) | Identical to (e) in outcome; it is the honest description of (e)'s mechanism. Worth naming because it shows (e) is *cheap*, not because it is *right* |

### The backward-compatibility cost of removing silent auto-unlock — stated explicitly

This is the load-bearing number and it is **currently unknown**:

- **If the current write path works** (i.e. §0.2's prediction is wrong — say `flash_util_byte_flipping` is slow enough that the sequence degenerates into data writes and the poll passes): silent auto-unlock is what makes **84 chips (75 `supported`)** writable today. Removing it per option (c) is a breaking change for every AT28C user, against a backdrop of **two already-open community issues about AT28C writes not working**. It would require a breaking-change note in both READMEs (the v1.20 precedent). Note that v1.20's breaking removal was defensible *precisely because* the removed path was dead code for all 746 chips — the opposite of this case.
- **If the current write path aborts** (§0.2's prediction holds): the backward-compatibility cost of *any* option is **zero**, because there is nothing working to preserve. Option (c) becomes affordable, and (b)/(d) become free.

**Therefore: sequence the milestone so the first phase settles §0.2 natively, and make the policy REQ conditional on that finding.** Writing the policy REQ before that test is writing it blind.

### Recommendation

**Adopt option (d): auto-unlock stays the default, becomes reported, and gains an explicit opt-out. Offer the protected attractor as an opt-in flag (F9), never a default.** Rationale, in priority order:

1. **The attractor should be the state the user can recover from.** A chip left unprotected can always be re-locked. A chip left protected silently fails the *next* write from any tool that lacks the prefix — which is the exact defect this milestone exists to fix. Protected-by-default would industrialise gh#12.
2. **Unprotected-attractor is self-evidencing; protected-attractor is not.** The `write` + `verify` that just succeeded *is* the proof the unlock worked. A re-lock claim can never be substantiated on this family (§4) — so a default that makes an unverifiable promise is a worse default.
3. **The standing posture is satisfied on substance.** The objection recorded in the backlog triage — "unlock … must never sit silently on every write" — has two readings. Option (d) honours the *visibility* reading in full (F3), and honours the *opt-in* reading where it actually matters: **unlock as a standalone, chip-state-mutating operation does sit behind explicit opt-in** in the `dev` group (F2), and the destructive `dev test` path stays behind the v1.21 gate. What (d) declines is *breaking a working write path for 84 chips* in the name of a posture aimed at a different risk.
4. **Both comparable tools auto-unlock by default.** flashrom "automatically tries to disable WP before any operation on a chip." minipro's older CLI defaults to *both* halves (`-u` = "Do NOT disable write-protect", `-P` = "Do NOT enable write-protect"). Deviating loudly needs a stronger reason than symmetry.
5. **The maintainer's own constraint.** gh#12, henols: *"Since it's a rear behavior of a chip I don't want it over shadow more common functionally."* Option (c) makes a rare chip state gate the common operation.
6. **Factory default is unprotected.** Datasheet p. 10: "the AT28C256 is shipped with SDP disabled." The unprotected attractor *is* the factory state — the least surprising resting place.

**Explicit residual risk accepted by (d):** a user who deliberately locked a chip, then runs `write` without reading the output, gets an unlocked chip. Mitigations: F3 makes it visible, F8 makes it avoidable, and the docs state it. If the operator judges that residual unacceptable, the next-best option is **(d) with an interactive TTY confirm on the unlock** — which keeps non-interactive/CI behaviour unbroken while making the interactive case opt-in. That is a strictly better fallback than (c).

---

## 3. Naming and CLI grammar

### What comparable tools call it

| Tool | Vocabulary | Polarity | Source confidence |
|---|---|---|---|
| **flashrom** | `--wp-status`, `--wp-enable`, `--wp-disable`, `--wp-range`, `--wp-region` | Auto-disable before any operation; state exposed via a **separate read-only status command**, not in write output | MEDIUM (cross-checked docs + list archive) |
| **minipro** (wholder/MiniPro, older TL866 CLI) | `-u` = "Do NOT disable write-protect"; `-P` = "Do NOT enable write-protect" | Both halves **default ON**, opt-**out** | MEDIUM (verbatim help text) |
| **minipro** (DavidGriffith fork, current) | `-u, --unprotect` = "Disable protection before programming"; `-P, --protect` = "Enable protection after programming" | Reads as opt-**in** action flags | MEDIUM (man page) |
| **AT28C datasheet** | "Software Data Protection" / "SDP" / "Write-Protect state" | n/a | HIGH |

**Two findings worth carrying into requirements.** First, the canonical tool **reversed its own polarity between generations** — so there is no "industry standard polarity" to appeal to, and any claim that one polarity is expected is unfounded. Second, the *vocabulary* is stable across both: everyone says **protect / unprotect** or **wp**. Nobody says **lock**.

### Fit to this project's Click grammar

In-tree precedent, read from `cli_handlers.py`:

- The `dev` group holds **8 sub-commands** (`read`, `reg`, `addr`, `consistency-check`, `write-cycle`, `fault-inject`, `validate-family`, `test`) and uses **hyphenated multi-word names**.
- `dev` is **community-facing**, not hidden — v1.21 shipped `dev test` to the community with a doc (`doc/community-validation.md`). Nothing in the group is `hidden=True` except two `-t/--timeout` options.
- **Both flag polarities already coexist deliberately** (D-13.3, documented in the `write` and `erase` docstrings): `write -b/--no-blank-check` is opt-out; `erase -b/--blank-check` is opt-in. So neither polarity is foreign here.
- The emergent in-tree rule that actually discriminates them: **`--no-X` skips a *check*** (`--no-blank-check`); **`--skip-X` skips a *chip-state-modifying operation*** (`--skip-erase`, added by Phase 92 / HARD-01 precisely to decouple a modifying step from a check).

### Recommendation

**Surface:** put the explicit operations in the **`dev` group**, not at top level.

```
firestarter dev sdp <chip> <enable|disable>     # click.Choice positional
```

- Honours the maintainer's "don't overshadow more common functionality": **one** new line in `firestarter --help`'s `dev` entry rather than two new top-level commands next to `read`/`write`/`erase`.
- Matches the group's existing multi-word/positional-argument style (`dev reg MSB LSB CTRL`, `dev addr CHIP ADDRESS`).
- `dev` being community-facing means this is genuinely discoverable and documentable — it is not a hiding place.
- Two-subcommand alternative (`dev sdp-lock` / `dev sdp-unlock`) is also grammatical and gives each half its own help text and gate; it costs a second help line. Either is defensible — state the choice, do not leave it implicit.

**Noun:** use **`sdp`**, not `lock`, not `wp`.
- `sdp` is the datasheet's own term and is **family-honest** — it names the specific `protection_kind` (`software_data_protection` in the seed's taxonomy) rather than over-claiming across the boot-block / sector-protection / OTP mechanisms catalogued in `doc/lockable-proms.md`.
- It keeps the naming lane clear for the out-of-scope seed: **per-family *action* verbs use the mechanism's name (`sdp`); the future cross-family *status* reader keeps `lock-status`.** That split is coherent rather than accidental, and it is worth recording as a decision so v1.22 does not squat on the seed's vocabulary.
- `wp` would borrow flashrom's noun for a mechanism that is not flashrom's WP-register model.

**Flags on `write`:**
- `--skip-sdp-unlock` for the opt-out (F8) — matches `--skip-erase` under the in-tree rule above, because SDP-unlock *modifies chip state*, it is not a check.
- `--sdp-relock` for the post-write lock (F9) — minipro's `-P/--protect` semantics, opt-in only.
- Reject `--no-sdp-unlock`: reads as a check-skip and invites the Phase-92 conflation that HARD-01 was created to remove.

---

## 4. Observability — what a trustworthy report looks like

### The constraint

SDP state is **not readable** on this family. Three independent sources agree: the AT28C256 datasheet defines no status bit; `doc/lockable-proms.md` §17 lists "Atmel AT28C16/64/256 — Usually no explicit SDP flag"; and the seed's own investigation note found minipro's `infoic.xml` cannot supply it either. **Confidence: HIGH.**

So no report may ever print "SDP: enabled ✓". The honest vocabulary is three-valued: **what we commanded**, **what we can infer**, **what we cannot know**.

### Recommended report shape

Reuse the v1.21 honest-fallback machinery rather than inventing a parallel one:

- **`NOT_MEASURED` precedent** — `diagnostic_report.py:59`: `NOT_MEASURED = "not measured"  # D-03: honest fallback, never a false 0`, substituted in exactly **one** place (`_transport_dict` / `_voltage_dict`) so there is no second hand-maintained field list. Add an analogous `SDP_STATE_NOT_READABLE = "not readable on this family"` sentinel with the same single-substitution discipline.
- **`is_submittable` precedent** — a field that can honestly read `None` on a perfectly good report must **not** gate submittability. An unconfirmable SDP state must never block a `--submit`.
- **`ladder_state` precedent** — a derived, advisory, report-side-only label that never writes back to the DB. An SDP finding is the same shape: it informs a human, it does not change `support_status`.

Concretely, three fields rather than one boolean:

| Field | Values | Meaning |
|---|---|---|
| `sdp_command_issued` | `"enable"` / `"disable"` / `null` | What the host asked the firmware to do. Always knowable |
| `sdp_sequence_ack` | `"ok"` / `"timeout"` / `"error:<code>"` / `null` | Whether the *firmware-side* sequence completed its write cycle. Knowable **once §0.2's inverted poll is replaced** |
| `sdp_state_after` | `"not readable on this family"` / `"inferred:on"` / `"inferred:off"` | Default is the honest refusal. Only F11's write-probe may populate `inferred:*`, and the `inferred:` prefix must be literal in the output — never collapsed to `on`/`off` |

### Replacing the inverted proof (F4)

The available honest signals, best to worst:

1. **`DATA` polling / toggle-bit on the sequence's own write cycle** (datasheet p. 10: `I/O7` returns the complement of the last byte written during `tWC`; `I/O6` toggles). This proves *a write cycle occurred and completed* — which is genuine positive evidence the device accepted the sequence — without asserting anything about the resulting SDP state. **This is the correct replacement for the `0x5555 == 0x20` poll.** Note the current poll's *shape* (`eeprom28c_wait_for_write` compares against expected array data) is unsuitable; polling must key on the complement/toggle semantics, not on array equality.
2. **Round-trip behavioural proof, destructive only:** after `disable`, an unprefixed write to a scratch byte should land; after `enable`, it should not. This is F11 and is the *only* thing that actually observes SDP state — hence `inferred:`, `--destructive`, and lockable-proms.md's explicit exclusion of it from "readable."
3. **Nothing else.** Absence of an error is not evidence. The report must say so.

### The reporting line for the in-write unlock (F3)

One line at INIT, in the same register as the existing flag echo (`Can erase: 1`, `Skip erase: 0`, visible in gh#12's pdr0663 log):

```
SDP: unlock sequence issued before write (chip left unprotected; --skip-sdp-unlock to preserve)
```

It states the action, the resulting attractor, and the escape hatch — and it makes zero claim it cannot back.

---

## 5. Interaction with the chip-ID / A9-12V mechanism

**Current state.** `eeprom28c_write_init` checks identity *before* SDP-disable, with the ordering decision documented in the source (`eeprom_28c.cpp:93-94`): "*Check chip identity via A9-12V (SAF-05) BEFORE SDP-disable (D-08: fail-fast on identity leaves the chip write-protected on mismatch).*"

**Three findings.**

1. **The ordering decision is currently a no-op.** All 84 `0x0D` chips have `chip_id_check: false` / `chip_id_value: 0x00000000`, so `if (handle->chip_id > 0)` never fires. D-08 has never taken effect on real silicon. Any v1.22 requirement that *relies* on it is relying on dead code.

2. **D-08's rationale generalises correctly to lock, and the generalisation is "fail before acting," not "leave protected."** Read literally, D-08 says the safe residual state is *protected*. For a lock operation that reasoning would invert (a mismatch abort leaves the chip *unprotected*). But the invariant that actually matters is the weaker and correct one: **identity is checked before any state-mutating sequence is issued, so a mismatch is a clean no-op in either direction.** Requirements should be written against that invariant, not against "leaves the chip protected" — otherwise the lock path inherits a rationale that does not apply to it.

3. **The genuine hazard is different, and it is a DB hazard, not an ordering hazard.** The A9-12V area on AT28C is **64 user-writable EEPROM bytes**, not a factory signature (datasheet p. 11). A virgin part reads `0xFFFF`. So:
   - Do **not** populate `chip_id_value` for AT28C to "activate" the check (anti-feature A4) — it would make every factory-fresh part fail identity, converting a dead check into an active false-negative across 84 entries.
   - Note that the ID area is itself inside the protected space ("written to or read from **in the same manner as the regular memory array**"), so *writing* an ID on a locked chip needs the prefix too. Reading it does not — reads are unaffected by SDP.
   - Driving 12V on A9 against a locked chip is electrically harmless; SDP gates writes, not reads.

**Recommended ordering for each new operation:**

| Operation | Order |
|---|---|
| `dev sdp <chip> disable` | identity (no-op today) → issue disable → poll write cycle → report `state_after: not readable` |
| `dev sdp <chip> enable` | identity (no-op today) → issue enable → poll write cycle → report `state_after: not readable` |
| `write` (default, option (d)) | identity → **unlock** → blank-check → page writes → verify. Unchanged shape; only the proof step and the report line change |
| `write --sdp-relock` | identity → unlock → blank-check → page writes → verify → **lock only if verify passed** |

That last conditional is the Phase 112 lesson repeating: `OP_VERIFY` had to be gated `if destructive:` (fix `7a74fcc`) because an unconditional step in a conditional pipeline is a latent bug. A re-lock after a *failed* verify strands the user with a locked chip they cannot retry on without discovering `dev sdp`.

---

## 6. The two community reports — what each reporter actually asked for

### gh#12 — "AT28Cxxx Write Protection Enable/Disable missing" (humbertocsjr, 2024-09-15, **OPEN**, no label)

Reporter's own words:

> "ATMEL eeprom chips (eg.: AT28C64, AT28C256, AT28C512...) have Data Protection feature, and can enable or disable data writing using a sequence of readings and writings of values on specific addresses."
>
> "On my chip I created a specific arduino circuit to send **'Software Data Protection Disable Algorithm'** before I can use firestarter for the first time, after this I used AT28C256 normally with firestarter."

**Expressed expectation:** a **one-time unlock** capability, so the second Arduino becomes unnecessary. He did **not** ask for lock. He did **not** ask for re-lock. He did **not** ask for status. His chip arrived protected; once unlocked, plain `write` worked for him.

**What satisfies gh#12: F2 alone.** One explicit unlock command. Everything else in this milestone is the maintainer's own scope, not his.

The thread also contains **the maintainer's framing of this milestone's central question**, in his words:

> "Cool that you have tried a chip like that! **What is the behavior you are expecting or how do you want it to work? Always unlock, write and lock the chip again? A special command for unlocking and locking?** What is the use cases you can see?
>
> Since it's a **rear** [rare] **behavior of a chip I don't want it over shadow more common functionally.**"

The reporter never answered. That question is unresolved *upstream*, and the second sentence is a standing design constraint from the project owner — it is the strongest single argument for the `dev`-group placement in §3 and against option (c) in §2.

**Three more voices accumulated on the same thread**, each an independent AT28C data point:

- **AndersBNielsen** (RURP hardware author): *"The most important part is to make sure firestarter doesn't try to put VPP on any pin... Doing its.. Firestarting."* — the 5V-only safety concern. Already satisfied: `0x0D` is VPP-free and the WARNING-5 override exists precisely to keep 12V off pin 1 for this family. Worth *saying* in the closeout comment.
- **pdr0663** (app 1.3.44, FW 1.4.2:uno, RUEP V2, Windows 11): AT28C256 write dies with a serial `PermissionError` at `0x0000/0x0200` — *"I see plenty of activity over the serial port before this happens, but it seems to write nothing before crashing."* Maintainer: *"I must disappoint you I haven't had the time to get the 28cXXX to work yet."* — **a second independent "AT28C256 write does not work" report, with nothing written.** Consistent with §0.2's INIT-abort prediction, though the transport is 1.x-era pre-COBS so it is corroborating, not conclusive.
- **No-Hazmats:** bought 2K×8 parts (the AT28C16 class — the 9 `adapter-required` DIP24 entries) and *"experienced this issue when I tried to erase and write to them."* AndersBNielsen redirected him to the W27C512. Note **"erase"** — see §0.4's phantom-erase gap.

### gh#11 — "Issues with AT28C256 Reading / Writing" (datapaganism, 2024-09-26, **OPEN**, no label)

Reporter's own words:

> "Reading the eeprom after writing to it reveals that **only some of it has been properly burned.**"
>
> "Is the setup of my programmer, I believe I have set the jumpers correctly. Given that I can burn and read it, its not 100% dead is it? … **Am I doing something wrong?**"
>
> `firestarter write at28c256 .\1.bin` → `File sent successfully in 339.49 seconds`

**Expressed expectation:** `write` should just work, and a read-back should match. He never mentions SDP — he does not know it exists. He is not asking for a new command; he is asking for the existing one to be **correct**, and secondarily for **a diagnosis** ("am I doing something wrong?").

**What satisfies gh#11:** a correct write path plus a `verify` that either passes or **explains**. Partial-write-reported-as-"successful" is the failure mode to eliminate — that is F4's real user value.

**Diagnostic caution for requirements:** his symptom is **not** diagnostic of SDP on its own. Partial-write-with-no-error *is* the SDP signature, but 339 s also indicates byte-at-a-time programming (the pre-page-write code path that no longer exists), and app 1.0.13 predates the entire 3.0.0 transport. Do **not** write a requirement that treats "gh#11's symptom disappears" as proof the SDP work landed — it conflates three candidate causes. He then got blocked upgrading (an unrelated f-string `SyntaxError` on Python 3.8 in 1.1.20) and never re-tested. A re-test ask was posted 2026-07-27; gh#12 has still had no maintainer response to the *feature* question.

### Closeout content that would actually serve them

| Issue | Say this |
|---|---|
| gh#11 | The 339 s byte-at-a-time path is gone (64-byte page write); the transport is rebuilt (COBS + CRC8); ask for `firestarter dev test at28c256` output — and **fix F12 first**, or his report auto-tags `community-fail` on a phantom erase step |
| gh#12 | Answer the maintainer's own 2024 question with the decided policy (§2), state that SDP-disable has shipped since `3.0.0b11`, name the new `dev sdp` surface, and confirm AndersBNielsen's VPP concern is structurally handled |

---

## 7. Anti-features — what NOT to build

1. **`firestarter lock-status <chip>` + the hand-curated protection table.** Out of scope per `PROJECT.md`; stays planted at `.planning/seeds/lock-status-command-hand-curated-protection-table.md`. **Genuine dependency to flag, not to scope back in:** because SDP state is unreadable, v1.22 **cannot** implement "leave it as you found it" (A3) or a pre-flight "this chip is locked, expect a partial write." Those two capabilities are *blocked*, not merely deferred. v1.22 is not crippled by the boundary **provided** it (a) chooses a deterministic attractor instead of promising as-found (§2), and (b) reports the honest refusal instead of a guess (F5). If a requirement ever needs true as-found restoration, that requirement belongs to the seed's milestone — say so in the REQ rather than approximating it.

2. **AMD Autoselect and Winbond product-ID protection-state query sequences.** Declared out of scope in `PROJECT.md`. They are the seed's firmware axis, and they are a different `protection_kind` (`sector_protection` / `boot_block_lock`) from SDP.

3. **Auto-relock by default** (A2) and **"leave as found" as a default** (A3) — §2 and §1.

4. **Populating `chip_id_value` for the AT28C family** (A4) — §5.

5. **A generic `locked` DB boolean** (A6) — `doc/lockable-proms.md` closing rule.

6. **Extending SDP handling to the other SDP families in v1.22** — AT29C, SST39SF (`0x06`), W29EE / `0x05`. Those handlers have their own SDP sequences with v1.15/v1.17 bench evidence attached (including the W29C040 permanently-locked boot block, which is a *different* mechanism entirely). Touching them re-opens settled evidence and multiplies the no-silicon problem. **Scope to `0x0D` only.**

7. **Implementing the datasheet's 6-byte software chip-erase** (p. 11) as part of the F12 fix. It is a genuine missing feature for `0x0D` and it would close No-Hazmats' complaint — but it is an *erase* feature riding in on an *SDP* milestone. Prefer the cheap honest fix (stop planning an erase step the firmware cannot serve) and file the chip-erase as a follow-up.

8. **Deleting `FLASH_ENABLE_WRITE_PROTECTION` as a dead duplicate.** It is the write-through prefix (§0.3). The abandoned v1.16 commit `0052c42` that tried this must not be resurrected. If dedup is desired, dedup toward *one* table with *two* documented names/uses — do not delete.

9. **Shipping the policy change without a documented behaviour note.** v1.20's precedent is a breaking-change section in **both** READMEs. Even option (d)'s additive change alters observable output for 84 chips.

---

## Feature Dependencies

```
F6 (native harness + RED test for §0.2)
    └──gates──> the §2 policy decision      [the backward-compat cost is unknown until F6 runs]
                    └──gates──> F3 (report the unlock)
                    └──gates──> F8 (--skip-sdp-unlock)

F4 (honest proof; replaces the inverted 0x5555 poll)
    └──requires──> F6
    └──enables──> F3, and every honest claim in F5

F1 (SDP-enable firmware)  ─┐
                           ├──share──> one new CMD arm + dual-repo lockstep (constants.py <-> firestarter.h)
F2 (SDP-disable standalone)─┘
    └──both required by──> `dev sdp <chip> <enable|disable>`   [§3]

F9 (--sdp-relock) ──requires──> F1  AND  the prefixed-write path (§0.3)
                  ──must be gated on──> verify success        [Phase 112 `if destructive:` lesson]

F5 (honest "not readable") ──reuses──> v1.21 NOT_MEASURED / is_submittable / ladder_state patterns

F11 (write-probe inference) ──requires──> v1.21 --destructive gate (SAFE-01: CLI-only, TTY confirm, SAFE-02 orchestrator-only)
                            ──conflicts with──> F5's default   [must never overwrite the honest refusal silently]

F10 (dev test SDP step) ──requires──> F1, F2, F5
                        ──perturbs──> dedup_fingerprint for ALL 0x0D chips  [cross-report N>=2 agreement]

F12 (phantom-erase gap)  ──blocks──> F7's value    [without it, every re-test report auto-tags community-fail]

A1 (lock-status + curated table)  ──blocks──> A3 ("leave as found")   [permanently, not just in v1.22]
```

### Dependency notes

- **F6 gates the policy decision, not just the code.** The single highest-leverage sequencing choice in this milestone is to make the first phase answer "does an AT28C write currently succeed or abort?" natively. Every §2 trade-off weight moves depending on the answer.
- **F1 and F2 are one plumbing job.** Same CMD arm, same lockstep, opposite table. Splitting them across phases doubles the wire-contract work.
- **F11 conflicts with F5 by construction.** F5's whole value is refusing to claim. F11 produces a claim. They coexist only if the `inferred:` prefix is literal and non-collapsible in both the rich table and the JSON block.
- **F10 has a quiet cost.** `dedup_fingerprint` walks `report.results` per step, so adding an SDP step changes the fingerprint of every `0x0D` report. Zero pre-existing AT28C reports makes this free *today* — record it as a decision so it is not discovered later.
- **F12 is small and load-bearing.** It is the difference between the gh#11/#12 closeout producing usable evidence and producing a spurious `community-fail`.
- **A1 permanently blocks A3.** Not a v1.22 sequencing artefact — you cannot restore an unreadable state in any milestone without the readable-families table, and AT28C is not a readable family even then.

---

## MVP Definition

### Launch with (v1.22)

- [ ] **F6** — native golden-trace harness + an explicit RED test for the §0.2 inverted proof. *Essential: it is the oracle, and no AT28C silicon exists.*
- [ ] **F4** — replace the `0x5555 == 0x20` poll with a defensible completion proof. *Essential: today's proof can only pass when the sequence failed.*
- [ ] **F1** — SDP-enable wired in firmware. *Essential: the declared milestone goal; the table exists with zero callers.*
- [ ] **F2** — SDP-disable as a standalone operation. *Essential: the only thing gh#12 actually asked for.*
- [ ] **`dev sdp <chip> <enable|disable>`** — the host surface (§3). *Essential: F1/F2 are unreachable without it.*
- [ ] **F3** — report the in-write auto-unlock. *Essential: converts "silent" to "observable" — the substance of the standing posture, at near-zero cost.*
- [ ] **F5** — honest `not readable on this family` state reporting. *Essential: the alternative is a fabricated success.*
- [ ] **The §2 policy decision, recorded with its backward-compat cost stated.** *Essential: it is the milestone's central UX decision and must not be arrived at implicitly.*
- [ ] **F7** — gh#11 / gh#12 closeout comments. *Explicitly best-effort; no requirement depends on a reply.*

### Add after validation (in-milestone, if capacity allows)

- [ ] **F8** `--skip-sdp-unlock` — trigger: the §2 decision lands on (d). Cheap, but needs the flag-bit audit.
- [ ] **F12** phantom-erase gap for `0x0D` — trigger: before the gh closeout comments go out, or the re-test reports are poisoned.
- [ ] **F9** `--sdp-relock` — trigger: F1 is proven native-green and the prefixed-write path exists.

### Future consideration (v1.23+)

- [ ] **F10** `dev test` SDP step — defer: touches the locked D-03/D-04 outcome ladder and perturbs `dedup_fingerprint`; worth its own decision record.
- [ ] **F11** write-probe SDP inference — defer: the only real state observation available, but destructive, and honest labelling is a design problem rather than a coding one.
- [ ] **A1** `lock-status` + curated protection table — deferred by declaration; stays in the seed.
- [ ] **Datasheet 6-byte software chip erase for `0x0D`** — an erase feature, not an SDP feature; would close No-Hazmats' gh#12 comment.
- [ ] **SDP handling for the other SDP families** (AT29C, SST39SF, W29EE) — deferred: multiplies the no-silicon problem across settled bench evidence.

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---|---|---|---|
| F4 honest proof (replace inverted poll) | HIGH | MEDIUM | **P1** |
| F6 native harness + RED test | MEDIUM (HIGH to the project) | MEDIUM | **P1** |
| F2 standalone unlock | HIGH (the only asked-for feature) | LOW–MED | **P1** |
| F1 SDP-enable firmware | MEDIUM | LOW–MED | **P1** |
| `dev sdp` host surface | HIGH | LOW–MED | **P1** |
| F3 report the in-write unlock | HIGH | LOW | **P1** |
| F5 honest "not readable" | HIGH | LOW | **P1** |
| §2 policy decision recorded | HIGH | LOW (decision, not code) | **P1** |
| F7 gh closeout | MEDIUM | LOW | **P1** (best-effort) |
| F12 phantom-erase gap | MEDIUM (HIGH for F7's value) | LOW–MED | **P2** |
| F8 `--skip-sdp-unlock` | MEDIUM | LOW | **P2** |
| F9 `--sdp-relock` | LOW–MED | LOW–MED | **P2** |
| F10 `dev test` SDP step | MEDIUM | MEDIUM | **P3** |
| F11 write-probe inference | MEDIUM | MED–HIGH | **P3** |

---

## Competitor Feature Analysis

| Feature | flashrom | minipro (both forks) | Recommended Firestarter approach |
|---|---|---|---|
| Auto-unlock before write | Yes, implicit and silent ("automatically tries to disable WP before any operation") | Yes by default in the older CLI (`-u` = *do not* disable); opt-in in the current fork | **Yes by default, but reported** (F3) — the differentiator |
| Opt-out of auto-unlock | Not documented | `-u` in the older CLI | **`--skip-sdp-unlock`** (F8) |
| Re-lock after write | No | Yes — default in the older CLI, `-P/--protect` in the current fork | **Opt-in only** (`--sdp-relock`, F9). Never default: unverifiable + manufactures the gh#12 bug |
| Standalone lock/unlock | `--wp-enable` / `--wp-disable` (top-level) | Flags on the write operation only | **`dev sdp <chip> <enable\|disable>`** — group-scoped per the maintainer's "don't overshadow" constraint |
| Read protection state | `--wp-status` (WP registers *are* readable on SPI parts) | Not exposed | **Honest refusal** (F5) — AT28C has no status bit. Cross-family status reader stays in the seed |
| Naming | `wp-*` | `protect` / `unprotect` | **`sdp`** — datasheet term, family-honest, leaves `lock-status` free for the seed |
| Honest "cannot confirm" | Not surfaced; docs tell users to check separately | Not surfaced | **First-class** — reuses v1.21's `NOT_MEASURED` discipline. The clearest differentiator in the milestone |

---

## Open Questions for Requirements

1. **Does an AT28C write currently succeed or abort on `3.0.0b11`?** (§0.2) — gates the §2 cost model. Native-answerable; must be phase 1.
2. **One `dev sdp` subcommand with a `click.Choice` positional, or two (`dev sdp-lock` / `dev sdp-unlock`)?** Both grammatical; the first shows one help line, the second gives each half its own gate text.
3. **New CMD code (9/10 free) or a new flag bit (byte full; `ctrl_flags` is `uint32_t` so `0x100` works firmware-side)?** CMD code looks cheaper; the flag path needs an 8-bit-assumption audit across the host emit path.
4. **Does the standalone `dev sdp` need the v1.21 `--destructive` gate, or is a TTY confirm sufficient?** Note SDP-enable/disable **do not modify array data** (datasheet p. 16 note 2) and are command-reversible — so the honest risk is "your chip stops/starts accepting writes," not data loss. The v1.21 gate was built for chip-sacrificing operations. Reusing it verbatim may be over-gating; inventing a second gate is worse. Decide explicitly.
5. **Does F12 get the honest-plan fix or the real `CMD_ERASE` arm?** Cheap-and-in-scope vs. closes a real gap.
6. **Is the residual risk in option (d) acceptable, or does the interactive-confirm fallback apply?** (§2, end.)

---

## Sources

**Primary — code and data read directly (HIGH confidence)**
- `/workspaces/firestarter/src/proms/eeprom_28c.cpp` — the `0x0D` handler; SDP-disable call site, the `0x5555` poll, the D-08 ordering comment
- `/workspaces/firestarter/include/flash_utils.h` — `FLASH_ENABLE_WRITE_PROTECTION` (zero callers) and `FLASH_ENABLE_WRITE` (byte-identical)
- `/workspaces/firestarter/include/firestarter.h` — CMD codes (9/10 free), flag byte fully allocated, `ctrl_flags` is `uint32_t`
- `/workspaces/firestarter/src/operation_utils.cpp` — `op_execute_function` returns false on a NULL callback
- `/workspaces/firestarter_app/firestarter/cli_handlers.py` — Click grammar; `write` / `erase` flag polarities (D-13.3); `dev` group; `dev test` and its `--destructive` gate
- `/workspaces/firestarter_app/firestarter/diagnostic_report.py` — `NOT_MEASURED` (D-03), `is_submittable`, `dedup_fingerprint`, `build_db_diff` / `ladder_state`
- `/workspaces/firestarter_app/firestarter/chip_test.py` — `derive_plan`, `OP_ERASE` condition, `_DESTRUCTIVE_OPS`, `locked_destructive`
- `/workspaces/firestarter_app/firestarter/data/chip_database.json` — 84 chips on `algorithm: 13`; all `chip_id_check: false`
- `/workspaces/firestarter_app/doc/community-validation.md` — the graduation ladder and DISP-01 no-auto-graduate lock
- `/workspaces/firestarter_app/doc/lockable-proms.md` — §17 (28Cxxx SDP not readable), the "readable" definition, the anti-`locked`-field rule

**Primary — datasheet (HIGH confidence)**
- Microchip **AT28C256** data sheet DS20006386B (2020-2022), local copy `/workspaces/firestarter_app/datasheets/AT28C256.pdf` — §6 Device Operation p. 10–11 (SDP prose, write-through-while-protected, "data in the … command sequences is not written to the device", shipped-SDP-disabled, user-writable A9-12V ID area, optional chip erase), §6.11 p. 16 (enable algorithm + notes), §6.12 p. 17 (disable algorithm)

**Primary — community issues, read via `gh issue view` (HIGH confidence in the quotes)**
- [gh#11 — Issues with AT28C256 Reading / Writing](https://github.com/henols/firestarter_prom/issues/11) (datapaganism, 2024-09-26, OPEN)
- [gh#12 — AT28Cxxx Write Protection Enable/Disable missing](https://github.com/henols/firestarter_prom/issues/12) (humbertocsjr, 2024-09-15, OPEN; thread includes henols' design question, AndersBNielsen, pdr0663, No-Hazmats)

**Ecosystem — comparable tools (MEDIUM confidence; cross-checked, polarity genuinely split between forks)**
- [minipro man page (DavidGriffith fork)](https://www.mankier.com/1/minipro) — `-u/--unprotect`, `-P/--protect`
- [wholder/MiniPro help text](https://github.com/wholder/MiniPro) — `-u  Do NOT disable write-protect`, `-P  Do NOT enable write-protect`
- [flashrom — example of partial write-protection](https://www.flashrom.org/user_docs/example_partial_wp.html) and [flashrom WP documentation review thread](https://mail.coreboot.org/hyperkitty/list/flashrom@flashrom.org/message/YN3JLIFLNPYY5KY4QTSNSDCSEOMLKK3V/) — `--wp-status` / `--wp-enable` / `--wp-disable` / `--wp-range`; auto-disable before any operation

**Project context**
- `.planning/PROJECT.md` §Current Milestone v1.22 (scope, out-of-scope declarations, abandoned commit `0052c42`)
- `.planning/seeds/lock-status-command-hand-curated-protection-table.md` (the out-of-scope sibling — boundary respected)
- `.planning/ROADMAP.md` §999.18 / §999.19 (the promoting triage notes, superseded on the "no SDP path today" claim by §0.1)

---
*Feature research for: AT28C Software Data Protection lifecycle on protocol `0x0D`*
*Researched: 2026-07-27*
