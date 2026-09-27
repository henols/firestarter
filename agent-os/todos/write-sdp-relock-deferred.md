---
title: Land `write --sdp-relock` — deferred TWICE (v1.30 Phase 135, v1.32 Phase 150), tracked as Backlog 999.28
date: 2026-08-03
priority: medium
blocked_by: nothing technical — deferred by operator decision, not by a dependency. Every prerequisite already shipped (see "Nothing to redo" below). Promote via /gsd-review-backlog when a milestone slot is wanted.
resolves_phase: none  # Backlog 999.28 was PROMOTED 2026-08-18 into v1.32 Phase 150, then DEFERRED BACK 2026-08-20 at the discuss step. Cleared to `none` deliberately: pointing at 150 would make this todo look resolvable by a vacated phase number. Both vacated slots (v1.30's 135, v1.32's 150) stay unreused. RELOCK-01…06 + RELOCK-08 are back in the backlog; DATA-06 is NOT — it stayed in v1.32, re-homed to Phase 151.
---

## ⏸ SECOND DEFERRAL — 2026-08-20 (read this first)

Promoted 2026-08-18 into **v1.32 as Phase 150**, then deferred out again by operator decision on
**2026-08-20** during `/gsd-discuss-phase 150` — before the gray-area selection was answered, and before
any research, plan or CONTEXT.md existed. **Nothing was created**: no `.planning/phases/150-*/`
directory, no CONTEXT.md, no commits in either sub-repo. Operator's words: *"I don't want the relock
implementation right now. I will implement it later if it is requested later."*

**So everything below still applies, once, with three amendments:**

1. **RELOCK-08 came and went with the feature** — v1.32 added it (`write --help` pins updated
   deliberately) and it returns to Backlog 999.28. **DATA-06 did NOT return**: it was retained in v1.32
   and re-homed to **Phase 151**, resolving on its documented-advisory branch, which the deferral makes
   the only reachable one. A future promotion must **not** re-claim DATA-06 or re-open that fork.
2. **The outward-facing obligation below has now fired twice, and the second firing is harder.** v1.32's
   Phase 152 OUT-01/OUT-04 were amended on 2026-08-20 to describe a **second withdrawal** rather than a
   migration, and OUT-05's fail-provable claim gate gained a **fifth claim class** rejecting any outward
   text that names `write --sdp-relock` as shipped or available. **A future promotion must reverse that
   gate class in the same change that lands the feature** — otherwise the gate will reject the very
   release notes announcing it.
3. **Six measurements were taken on 2026-08-20 against app `9cc57c7`** and are recorded in
   ROADMAP §"Phase 150" → *Measured findings*, so a re-promotion needs no fresh archaeology: the
   `protect_on_after` distribution (70/746 true; 43 of 84 `algorithm: 13`; **27 of 27** `algorithm: 5`,
   i.e. a constant there); its `MP_PROTECT_AFTER` = *"can* re-protect after write" capability-not-policy
   semantics; the machine-proven element-wise equality between that field and `sdp_capability`'s
   transcription (`tests/test_sdp_db_invariant.py::test_sdp_partition_matches_infoic_derived_field_element_wise`);
   `tools/check_sdp_capability_invariants.py` Class 2(b) forbidding any binding of `SDP_CAPABLE_TOKENS`
   other than a literal `frozenset` of string literals (so "read the DB field at runtime" trips an
   existing gate); the **true** `write --help` pin locations —
   `tests/test_characterization.py::test_help_write` and `::test_no_blank_check_polarity`, two syrupy
   snapshots each carrying the full help text, **not** Phase 136's channel-gating tests, and `write` is
   not channel-gated at all; and the fact that the non-verbose log formatter is `"%(message)s"`
   (`cli_handlers.py:110`), so `logger.warning` emits **no** level prefix and RELOCK-04's "mandatory
   final `WARNING:` line" needs a **literal** `WARNING:` in the message string
   (`eprom_info.py:269` is the in-tree precedent).

Also still true and worth re-reading before promoting: the deleted `dev sdp` handler, with its four
ordered gates (absent-chip → capability → support-status → consent), is recoverable **verbatim** at
`firestarter_app` commit `259a0f0`, and `firestarter/sdp_honesty.py`'s module docstring still names
`write --sdp-relock` as its intended caller.

---

# `write --sdp-relock` was deferred out of v1.30 — and the deletion shipped without it

**Deferred 2026-08-03** by operator decision, while v1.30 Phase 132 was in flight at plan 08 of 09.
Scoped as **v1.30 Phase 135**, never planned, never executed — no `.planning/phases/135-*/` directory
was ever created. Filed as ROADMAP Backlog **999.28**, which carries the full goal, success criteria,
prerequisites and promotion constraints. **The v1.30 phase number was not reused:** Phases 136 and 137
keep their numbers and the 135 slot stays vacant, same convention as v1.13's Phase 75 → Backlog 999.4.

## Why this is a todo and not just a backlog stub

Because a **paired** change was split, and only one half shipped.

`REQUIREMENTS.md` §`write --sdp-relock` (RELOCK) opens with its own constraint:

> Must ship with the deletion — they are a pair, and deleting the lock before re-homing it strands the
> only legitimate use case the deleted command served.

v1.30 Phase 132 ships the deletion of `firestarter dev sdp <chip> enable|disable`. This half did not
ship with it. So **v1.30 strands exactly the use case that sentence names**, and the window stays open
until 999.28 is promoted:

- `write` auto-unlocks on every protocol-`0x0D` write (v1.22 policy (d), declinable via
  `--skip-sdp-unlock`) and **never re-locks**.
- The `dev sdp enable` surface is **gone**.
- ⇒ There is **no supported way to deliberately protect an SDP part**, and on `0x0D` the protection bit
  cannot be read back, so a user cannot observe the resulting state either.

That is an accepted cost, recorded in `REQUIREMENTS.md` §Out of Scope and ROADMAP §`Phase 135` /
§`Phase 999.28`. It is not a defect to fix — it is a **promise not to overstate**, which is what makes it
a live todo rather than a parked idea.

## The outward-facing obligation this creates for v1.30's own close

v1.30 Phase 137 (CLOSE-05, CLOSE-06) was amended on 2026-08-03 because both criteria previously
described a substitution that will not exist in the shipped release:

- **Release notes** must map `dev sdp disable` → `write` (automatic — real, the firmware auto-unlocks on
  every `0x0D` write), and `dev sdp enable` → **nothing in this release**: withdrawn, tracked as Backlog
  999.28. They must **not** map it to `write --sdp-relock`.
- **The gh#12 reply** must say the same thing. gh#12 asked for enable/disable; after v1.30 it gets
  `disable`-by-default and **no** `enable` at all. See the amended
  [`gh12-followup-after-dev-sdp-retirement.md`](gh12-followup-after-dev-sdp-retirement.md).

Announcing a command that does not exist in the release being announced is the same overclaim class as
v1.22's C-5 correction — the class v1.30's honesty ledger exists to catch. Getting this wrong would be
the milestone failing its own stated purpose in its most public artifact.

## What this todo owes, and when

1. **At v1.30's close (Phase 137)** — verify the release notes and the gh#12 reply describe a
   **withdrawal**, not a migration. This is the urgent half; it expires when v1.30 ships.
2. **Whenever 999.28 is promoted** — land the feature, then correct the record outward: the shipping
   version's release notes announce it, and gh#12 gets the follow-up it was promised. This half has no
   deadline.

## Nothing to redo at promotion time

Every prerequisite is already in the tree:

- Firmware `CMD_SDP_LOCK` / `CMD_SDP_UNLOCK` — v1.22 Phase 119. **Host-only work**: no firmware change,
  no dual-repo lockstep, no `.hex` re-cut.
- The capability gate to reuse — `sdp_capability()`.
- `eprom_operations.py` `sdp_unlock` / `sdp_lock` and their `COMMAND_NAMES` entries — kept deliberately,
  load-bearing for this caller. (Their dereference sites were re-measured by v1.30 plan 132-08 to
  `_setup_operation:329` / `_operation_context:405`; the older `:301`/`:377` citations are stale.)
- The D-10 honesty wording and D-14 unknown-command mapping — Phase 132 authored them into a shared
  production helper as an explicit **forward contract** for this caller (`132-CONTEXT.md` D-01), and
  `tests/test_sdp_honesty.py` is its stable module name (`132-03-SUMMARY.md:153` — no further rename
  owed).
- **Polarity already decided, do not re-litigate:** verify failure ⇒ **skip the relock and report it
  loudly**, leaving the recoverable state. Per v1.22 auto-unlock policy (d), recorded at
  `PROJECT.md:823`. Relocking a part whose write did not verify would protect a bad image behind a lock
  that cannot be read back and can only be cleared by another write.

## Constraints at promotion

- **One-writer-per-file.** This writes `firestarter/cli_handlers.py` in the `write` handler (~:570).
  Worktree isolation is unavailable while the code lives in the `firestarter_app` submodule — the
  executor commit protocol cannot commit into a submodule from an isolated worktree — so it cannot run
  concurrently with another phase writing that file. See ROADMAP §v1.30 "Dependency spine".
- **`write --help` changes.** Any `write`-help output pinned by v1.30 Phase 136's channel-gating tests
  must be updated **deliberately** as part of this work, not silently re-baselined.

## Related

- ROADMAP Backlog **999.28** — the promotable stub (full success criteria).
- ROADMAP §v1.30 `### Phase 135` — the deferral record and renumbering rationale.
- `REQUIREMENTS.md` §RELOCK — RELOCK-01…06 retained verbatim with `⏸` checkboxes; §Out of Scope carries
  the decision row.
- **RELOCK-07 did NOT come here.** The stale-label re-homing stayed in v1.30, re-homed to Phase 137, and
  its targets now name Backlog 999.28. It also carries a warning worth reading: four places in the
  record cite those two labels and no two agree.

---

## ◐ PARTIAL DISCHARGE 2026-08-21 — v1.32 Phase 152, plan 152-14. **THIS TODO STAYS IN PENDING.**

This note records that **one half** of §"What this todo owes, and when" is discharged. The other half is
**not**, and must not be presented as met.

**Discharged — the gh#12 follow-up half.** The reply owed on gh#12 is posted:
[issuecomment-5373440001](https://github.com/henols/firestarter_prom/issues/12#issuecomment-5373440001),
id `IC_kwDOSX4ER88AAAABQEgwAQ`, `2026-08-21T18:00:19Z`. It describes a **withdrawal spanning a second
release**, not a migration, and it never names `write --sdp-relock` — satisfying both this todo's
outward-facing obligation and the amended companion todo now at
`.planning/todos/completed/gh12-followup-after-dev-sdp-retirement.md`.

**NOT discharged — "the shipping version's release notes announce it."** That half is *unmeetable* until
the feature exists, and the feature does not exist. v1.32's release notes announce the **withdrawal**
and name Backlog 999.28; they do not announce the feature, because there is nothing to announce. Do not
read this partial discharge as closing that obligation.

**`resolves_phase` stays `none`.** Unchanged and deliberate, for the reason already recorded in the
frontmatter: pointing it at a vacated phase number (v1.30's 135 or v1.32's 150) would make this todo
look resolvable by a phase that never existed. Both slots stay unreused.

**The standing instruction survives, and v1.32 made it sharper.** A future promotion of Backlog 999.28
must **reverse OUT-05's fifth claim-gate class in the same change that lands the feature**, or the gate
will reject the very release notes announcing it. As of this phase that gate is no longer hypothetical:
`152-check-claims.py` is armed at seven real outward artifacts, its `sdp-relock-as-shipped` row is
proven to reject 11/11 planted overclaims while permitting 7/7 withdrawal phrasings, and its 34-leg
paired suite pins both directions. The reversal is therefore a real, testable code change with a named
owner — not a note to remember.

One implementation detail measured during this phase and worth carrying: the negative lookahead requires
the withdrawal word (`withdrawn|deferred|not shipped|not shipping|unavailable|absent`) to follow the
command name almost immediately. An intervening word breaks it — "`write --sdp-relock` **command** is
withdrawn" is rejected as an overclaim. Any reversal must account for that shape.
