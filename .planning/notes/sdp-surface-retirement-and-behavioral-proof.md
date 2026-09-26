# Retire `dev sdp`; prove the SDP lock behaviorally inside `dev test`

**Date:** 2026-07-31
**Context:** `/gsd-explore` session — "is the `dev sdp` option needed, does it bring any real value?"
**Status:** decided and **queued as the NEXT milestone after v1.23** (operator, 2026-07-31) — provisional
`v1.30 SDP Surface Retirement & Behavioral Lock Proof`, promoted from Backlog Phase 999.25, pending
`/gsd-new-milestone`. Scope this milestone from this note.
**Touches:** `firestarter_app` only (host). **No firmware change** — see §7.

> **⏸ AMENDED 2026-08-03 — part 3 of the "three parts, decided together" below did NOT ship.**
> This note was scoped into **v1.30**, Phases 131–137, on 2026-08-03. Part 3, `write --sdp-relock`
> (Phase 135), was then **deferred out of the milestone** by operator decision the same day and filed as
> ROADMAP Backlog **999.28**; the phase number was not reused, so v1.30's active set is 131–134 + 136–137.
> Parts 1 and 2 proceed as written here.
>
> **The consequence this note's own §1.3 predicts is therefore real:** part 3 is described below as *"the
> only legitimate user need the deleted command was serving (an AT28C programmed to sit in a live
> machine)"* — and part 1 ships without it. v1.30 **withdraws** that capability and replaces it with
> nothing until 999.28 is promoted. Read this note for the design, which stands unchanged; read
> ROADMAP §`Phase 135`, §`Phase 999.28`, `REQUIREMENTS.md` §Out of Scope, and
> `.planning/todos/pending/write-sdp-relock-deferred.md` for what actually shipped and what is owed
> outwardly because of it. Do **not** scope part 3 from this note as if it were in v1.30.
>
> *(Also stale above, left as-found: the `Status:` line still reads "queued … pending
> `/gsd-new-milestone`"; the milestone was activated 2026-08-03. And this note's `STATE.md:154` /
> `PROJECT.md:671` citations for the "v1.23+" labels are stale — measured 2026-08-03 the live lines are
> `STATE.md:634` / `PROJECT.md:823`. See RELOCK-07, which owns that fix and lists all four divergent
> citation sites.)*

---

## 1. The decision (operator, 2026-07-31)

Three parts, decided together:

1. **Delete `firestarter dev sdp <chip> enable|disable`** — the standalone command shipped in
   v1.22 Phase 120 (`cli_handlers.py:2095`, live in `3.0.0b14`).
2. **Move the proof into `dev test`** — for SDP-capable chips, lock the part, attempt a write
   *without* unlocking, and assert the chip is **unchanged**; then unlock and prove it is
   writable again. This is the first oracle the SDP lock has ever had.
3. **Keep the re-lock, as `write --sdp-relock`** — the already-deferred flag becomes the single
   user-facing way to deliberately protect a part. It is the only legitimate user need the
   deleted command was serving (an AT28C programmed to sit in a live machine).

## 2. Why `dev sdp` does not earn its place

- **`disable` is very nearly redundant.** Firmware auto-unlocks at the start of *every*
  protocol-`0x0D` write (`eeprom28c_write_init`; host side `eprom_operations.py:1637`), and since
  Phase 118 that is visible and declinable via `--skip-sdp-unlock`. A user holding an SDP-locked
  AT28C256 just runs `firestarter write` and it works. `dev sdp <chip> disable` is a second way to
  do what `write` already does unasked.
- **`enable` was the only non-redundant half — and the unverifiable one.** Protection state cannot
  be read back on this family (Phase 117 D-05, Phase 119 D-12), so the command's own success line
  claims only that the sequence was *emitted*. It is a state change no one can observe.
- **`0x0D` is still `UNVERIFIED`.** No AT28C part in operator inventory; nothing about either
  direction was ever proven on silicon.
- **The namespace was on a collision course with 999.15.** The resolved channel-split design gives
  **stable only `dev read` + `dev test`**, so `dev sdp` disappears from `pip install firestarter`
  anyway — while `constants.py:66` asserts the firmware commands are unconditional *"because they
  are real user-facing operations in every build."* Host and firmware disagreed about who the
  feature was for. Retiring the command and moving the capability into `dev test` (a stable
  survivor) and `write` (production surface) removes the contradiction instead of arbitrating it.

## 3. Why a `dev test` leg is the *only* possible oracle

On `0x0D` the protection bit is not readable, so protection is observable **only through its
effect**: a locked part must refuse to accept data. That makes lock→inhibited-write→read-back the
sole evidence path in existence for this feature. A standalone command can never carry it.

Three further properties make `dev test` the right host:

- It **already writes on every run** (Phase 121 D-04) and the AT28C family is written in full with
  no prompt, so the leg adds no new destructiveness class.
- It is the **community-validation entry point** — built precisely to validate chips on hardware
  the maintainer does not own — and it files a report through `submit_report` (DEVTEST-05/06). The
  evidence comes *back to the repo* instead of dying in a stranger's terminal.
- It **survives the 999.15 channel split into stable**, so the SDP lifecycle stays reachable to
  ordinary users as a test rather than as a footgun.

## 4. Leg design

**Applicability predicate:** `sdp_capability(chip_name, db) -> (bool, reason)`
(`firestarter/sdp_capability.py:266`) — the fail-closed allow-set derived from `infoic.xml` `flags`
bit 15, **43 ALLOW / 41 REFUSE of 84** `0x0D` chips. REFUSED chips get an `NA`/`SKIPPED` step
carrying `reason`, never a silent omission.

**Step order (all four steps, in this order):**

| # | Step | Assertion |
|---|------|-----------|
| 1 | write pattern A (auto-unlock as normal) + verify | baseline: the part is writable **before** any lock. Without this a locked-from-the-factory part reads as "lock works". |
| 2 | `sdp_lock` (CMD 10) | emission only — nothing observable yet |
| 3 | write pattern B with `FLAG_SKIP_SDP_UNLOCK`, then **read back** | **the oracle:** bytes must still equal pattern A |
| 4 | `sdp_unlock` (CMD 9) + write + verify | proves the part is writable again and leaves it unlocked |

**Constraint — the leg cannot be flag-gated.** `dev test` takes **zero options** since Phase 121
D-05 (`dev_test(app, chip)`, `cli_handlers.py:1958`); the four v1.21 flags were removed, not
disabled. So the leg must be **plan-derived** from the capability predicate, exactly like every
other step in `derive_plan`. Do not reintroduce an option for it.

## 5. Three traps this leg must dodge

**Trap 1 — it is a false-green magnet.** The load-bearing assertion is that a write *fails*, and
every unrelated failure (transport error, brownout, absent chip, blank-check abort) produces the
same non-zero result. This is the same class as the SAFE-04 absent-chip trap, where the real
assertion turned out to be `read_hardware_revision_value.assert_not_called()` rather than an exit
code. **The oracle must be read-back equality against pattern A** — "the write reported failure"
is not evidence. A *partial* change is gh#11's exact symptom and must read **BAD**, never OK.

**Trap 2 — keep the sensitivity pointing the right way.** If the lock never reaches silicon (the
v1.22 defect class), the inhibited write *succeeds* and the leg reports BAD. That is the entire
value of the leg. It must therefore never be allowed to downgrade to `SKIPPED`/`NA` because the
write unexpectedly succeeded — an unexpected success is the failure signal, not an inapplicable
step.

**Trap 3 — the run must end unlocked, and the report must say so.** Step 4 is not optional
bookkeeping: an abort between steps 2 and 4 (Ctrl-C, cable yank, brownout) ships a locked chip back
to a community member. Recovery exists — a plain `firestarter write` auto-unlocks — and the report
line must state it in those words. Note `0x0D` has **no erase operation at all**, so recovery is
"rewrite", never "erase".

## 6. Why deleting the command is safe

**Because auto-unlock is default-on.** A chip left locked by any means is recovered by a plain
`firestarter write`. There is no orphaned-chip path, and therefore no capability lost by removing
the standalone unlock. Without that property, removal would be reckless — record the dependency, so
that if auto-unlock's default is ever revisited, this decision is revisited with it.

## 7. Insertion points (host only)

**Delete:**
- `cli_handlers.py:2095-2227` — `dev_sdp` and its four gates
- `firestarter_app/tests/test_dev_sdp_cmd.py` — repurpose the gate-ordering cases onto the new leg
  where they still apply

**Keep, load-bearing for both survivors:**
- `eprom_operations.py:1736 sdp_unlock` / `:1784 sdp_lock` — the test leg and `--sdp-relock` both
  need them
- `constants.py:72-73` `COMMAND_SDP_UNLOCK`/`COMMAND_SDP_LOCK` **and their `COMMAND_NAMES` entries**
  — dereferenced at `eprom_operations.py:301` and `:377`; a missing entry is a `KeyError` at
  operation setup, not a cosmetic gap
- `sdp_capability.py` in full — now serving `write`'s D-04 auto-set, the new leg, and `--sdp-relock`

**Extend:**
- `chip_test.py:289-295` op vocabulary, `:636 _DESTRUCTIVE_OPS`, and `derive_plan` — new ops for the
  lock / inhibited-write / unlock steps. Every consumer that reads `StepResult.op` (the
  `dedup_fingerprint` hash, the report renderer) picks them up without learning a new field, which
  is exactly the D-06/D-07 rationale that admitted `OP_WRITE_PARTIAL`.
- `diagnostic_report.py` — report rows plus the recoverability line from Trap 3

**No firmware change.** `CMD_SDP_LOCK`/`CMD_SDP_UNLOCK` stay exactly as Phase 119 shipped them, and
the firmware is what the new leg exercises. This is a **single-repo change** — no dual-repo lockstep,
no `.hex` re-cut, no version-pair coupling.

## 8. `--sdp-relock` — and a stale label to fix

`--sdp-relock` was deferred **"to v1.23+"** (`STATE.md:154`, `PROJECT.md:671`). v1.23 has since been
activated as **PY32F071 Integration**, so that label now points at the wrong milestone and the flag
has no home. Phase 999.25 becomes its home; the two rows above should be corrected when the stub is
scoped, not silently left to be discovered.

**Corrected 2026-08-05, Phase 137 plan 137-04 (RELOCK-07, now Complete) — the terminal fix:** the
live lines, fresh-measured at this plan's execution, are `.planning/STATE.md:972` and
`.planning/PROJECT.md:844`, both now reading **Backlog 999.28** in place of "v1.23+". See
`REQUIREMENTS.md`'s RELOCK-07 for the full citation-drift history across all sites.

Design carried over from the v1.22 research and **not** re-decided here: the relock is opt-in only,
and the v1.22 research assumed it is **gated on verify success** (relocking a part whose write did
not verify would protect a bad image). That assumption is unconfirmed — see `research/questions.md`.

## 9. Costs accepted knowingly

- **A one-day-old public instruction is stranded.** `dev sdp` is named in the gh#12 reply and in the
  b14 app release notes, both dated 2026-07-30 (`122-GH12-COMMENT.md:15`,
  `122-RELEASE-NOTES-app.md:12,22`). Removal owes that thread a follow-up stating what replaced it —
  tracked as a pending todo. Not a silent disappearance.
- **gh#12 asked for "enable/disable" and gets neither by that name.** The unlock half is absorbed
  into `write`'s default behaviour and the lock half into `write --sdp-relock`. Defensible, but it
  is a *rewording of the reporter's own ask* and should be stated as such in the follow-up.
- **A breaking removal from a published pre-release surface.** `3.0.0b14` went to PyPI `--pre` on
  2026-07-30; the blast radius is one day of pre-release installs and no stable release ever carried
  the command. Cheap now, and strictly more expensive every week it waits.
